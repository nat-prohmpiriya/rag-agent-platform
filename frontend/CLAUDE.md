# Frontend - Claude Instructions

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Framework** | SvelteKit 2.x |
| **UI Library** | Svelte 5 (Runes syntax) |
| **Language** | TypeScript (strict) |
| **CSS** | Tailwind CSS v4 |
| **UI Components** | shadcn-svelte |
| **i18n** | Paraglide.js (@inlang/paraglide-js) |
| **Build** | Vite 7.x |
| **Adapter** | Static (SSG) |
| **Linter** | ESLint + Prettier |

---

## Project Structure

```
frontend/
├── src/
│   ├── app.html            # HTML template
│   ├── app.d.ts            # Global type definitions
│   ├── hooks.ts            # SvelteKit hooks (i18n setup)
│   │
│   ├── routes/             # Pages and layouts
│   │   ├── +page.svelte    # Home page
│   │   ├── +layout.svelte  # Root layout
│   │   └── [feature]/      # Feature pages
│   │
│   └── lib/
│       ├── components/
│       │   ├── ui/         # shadcn-svelte base components
│       │   └── custom/     # Custom business components
│       │
│       ├── stores/         # Svelte stores
│       ├── utils/          # Utility functions
│       ├── api/            # API client functions
│       ├── types/          # TypeScript types
│       └── assets/         # Static assets
│
├── messages/               # i18n translations
│   ├── en.json
│   └── th.json
│
├── static/                 # Public static files
└── tests/                  # Test files
```

---

## Svelte 5 Runes Syntax

### IMPORTANT: Use Runes, NOT Legacy Syntax

| Legacy (Svelte 4) | Runes (Svelte 5) |
|-------------------|------------------|
| `let count = 0` | `let count = $state(0)` |
| `$: doubled = count * 2` | `let doubled = $derived(count * 2)` |
| `$: { console.log(count) }` | `$effect(() => { console.log(count) })` |
| `export let name` | `let { name } = $props()` |
| `<slot />` | `{@render children()}` (Snippets) |
| `createEventDispatcher` | Callback props (`onclick={() => handler()}`) |

### State Management

```svelte
<script lang="ts">
  // Reactive state
  let count = $state(0);

  // Derived value
  let doubled = $derived(count * 2);

  // Side effect
  $effect(() => {
    console.log(`Count changed to ${count}`);
  });

  // Props with TypeScript
  let { title, onClick } = $props<{
    title: string;
    onClick?: () => void;
  }>();
</script>
```

### Component Events (Svelte 5 way)

```svelte
<script lang="ts">
  // Use callback props instead of createEventDispatcher
  let { onSubmit } = $props<{
    onSubmit: (data: FormData) => void;
  }>();
</script>

<button onclick={() => onSubmit(formData)}>Submit</button>
```

### Component Composition (Snippets)

**IMPORTANT:** Do NOT use `<slot />` - it is deprecated in Svelte 5. Use Snippets instead.

```svelte
<!-- Parent component defining snippet slots -->
<script lang="ts">
  import type { Snippet } from 'svelte';

  let { children, header } = $props<{
    children: Snippet;
    header?: Snippet;
  }>();
</script>

<div class="card">
  {#if header}
    <header class="card-header">
      {@render header()}
    </header>
  {/if}
  <main class="card-body">
    {@render children()}
  </main>
</div>
```

```svelte
<!-- Using the component with snippets -->
<script lang="ts">
  import Card from './Card.svelte';
</script>

<Card>
  {#snippet header()}
    <h2>Card Title</h2>
  {/snippet}
  <p>This is the card body content.</p>
</Card>
```

---

## UI Components (shadcn-svelte)

### Why shadcn-svelte?

- **Own your code**: Components copied to your project, fully customizable
- **Enterprise-ready**: Easy white-labeling and theme customization
- **No dependency lock-in**: No breaking changes from library updates
- **Tailwind-based**: Consistent with our CSS strategy

### Adding Components

```bash
# Initialize (first time only)
npx shadcn-svelte@latest init

# Add components as needed
npx shadcn-svelte@latest add button
npx shadcn-svelte@latest add card
npx shadcn-svelte@latest add dialog
npx shadcn-svelte@latest add input
npx shadcn-svelte@latest add table
```

### Usage

```svelte
<script lang="ts">
  import { Button } from '$lib/components/ui/button';
  import * as Card from '$lib/components/ui/card';
</script>

<Card.Root>
  <Card.Header>
    <Card.Title>Title</Card.Title>
  </Card.Header>
  <Card.Content>
    <p>Content here</p>
  </Card.Content>
  <Card.Footer>
    <Button variant="default">Save</Button>
    <Button variant="outline">Cancel</Button>
  </Card.Footer>
</Card.Root>
```

### Component Organization

| Location | Purpose |
|----------|---------|
| `src/lib/components/ui/` | shadcn-svelte base components |
| `src/lib/components/custom/` | Business-specific components (ChatWindow, DocumentViewer, etc.) |

### PII & Privacy UI

When rendering text with PII placeholders from the backend (e.g., `[PERSON]`, `[PHONE]`, `[EMAIL]`), apply distinct visual styles to indicate redacted data.

```svelte
<!-- src/lib/components/custom/PIIBadge.svelte -->
<script lang="ts">
  let { type, index } = $props<{
    type: 'PERSON' | 'PHONE' | 'EMAIL' | 'ADDRESS' | 'ID';
    index?: number;
  }>();

  const colors: Record<string, string> = {
    PERSON: 'bg-amber-100 text-amber-800 border-amber-300',
    PHONE: 'bg-blue-100 text-blue-800 border-blue-300',
    EMAIL: 'bg-green-100 text-green-800 border-green-300',
    ADDRESS: 'bg-purple-100 text-purple-800 border-purple-300',
    ID: 'bg-red-100 text-red-800 border-red-300',
  };
</script>

<span
  class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border {colors[type]}"
  title="Redacted for privacy"
>
  [{type}{index ? `_${index}` : ''}]
</span>
```

Use regex to detect and replace PII placeholders in chat responses:

```typescript
// src/lib/utils/pii.ts
export function parsePIIPlaceholders(text: string): (string | PIIToken)[] {
  const regex = /\[(PERSON|PHONE|EMAIL|ADDRESS|ID)(?:_(\d+))?\]/g;
  // ... parse and return array of strings and PIIToken objects
}
```

### SQL Review Component

For the Text-to-SQL feature, create a confirmation UI before executing queries:

```svelte
<!-- src/lib/components/custom/SQLReviewCard.svelte -->
<script lang="ts">
  import { Button } from '$lib/components/ui/button';
  import * as Card from '$lib/components/ui/card';
  import { highlightSQL } from '$lib/utils/highlight'; // shiki

  let { sql, estimatedRows, onExecute, onEdit } = $props<{
    sql: string;
    estimatedRows?: number;
    onExecute: () => void;
    onEdit: () => void;
  }>();

  let isExecuting = $state(false);
</script>

<Card.Root class="border-amber-200 bg-amber-50">
  <Card.Header>
    <Card.Title class="flex items-center gap-2">
      <span>Review Generated SQL</span>
      {#if estimatedRows}
        <span class="text-sm font-normal text-muted-foreground">
          ~{estimatedRows} rows
        </span>
      {/if}
    </Card.Title>
  </Card.Header>
  <Card.Content>
    <pre class="p-4 rounded-lg bg-slate-900 text-sm overflow-x-auto">
      {@html highlightSQL(sql)}
    </pre>
  </Card.Content>
  <Card.Footer class="flex gap-2 justify-end">
    <Button variant="outline" onclick={onEdit}>Edit SQL</Button>
    <Button
      variant="default"
      onclick={onExecute}
      disabled={isExecuting}
    >
      {isExecuting ? 'Executing...' : 'Execute Query'}
    </Button>
  </Card.Footer>
</Card.Root>
```

**Important:** Never auto-execute SQL. Always wait for explicit user confirmation.

---

## Coding Conventions

### File Naming

| Type | Convention | Example |
|------|------------|---------|
| Components | PascalCase | `UserCard.svelte` |
| Routes | lowercase with hyphens | `user-profile/+page.svelte` |
| Utilities | camelCase | `formatDate.ts` |
| Types | PascalCase | `User.ts` |

### Component Structure Order

```svelte
<script lang="ts">
  // 1. Imports
  import { Button } from '$lib/components/ui/button';
  import type { User } from '$lib/types';

  // 2. Props
  let { user, onSave } = $props<{
    user: User;
    onSave: (user: User) => void;
  }>();

  // 3. State
  let isLoading = $state(false);

  // 4. Derived
  let fullName = $derived(`${user.firstName} ${user.lastName}`);

  // 5. Effects
  $effect(() => {
    // side effects here
  });

  // 6. Functions
  function handleSubmit() {
    // ...
  }
</script>

<!-- Template -->
<div class="container">
  <!-- content -->
</div>

<!-- Styles (prefer Tailwind, use <style> only when necessary) -->
```

### TypeScript Rules

- Always use `lang="ts"` in script tags
- Define prop types explicitly with `$props<T>()`
- Use interfaces for complex types in `src/lib/types/`
- Avoid `any` type

---

## Tailwind CSS v4

### Key Differences from v3

- No `tailwind.config.js` - use CSS-based configuration
- Use `@theme` directive for customization
- New color syntax

### Enterprise Theming

```css
/* src/app.css */
@import 'tailwindcss';

@theme {
  /* Override for enterprise customization */
  --color-primary: #0066cc;
  --color-secondary: #6c757d;

  /* Custom brand colors */
  --color-brand-50: #eff6ff;
  --color-brand-500: #3b82f6;
  --color-brand-900: #1e3a8a;
}
```

---

## Internationalization (i18n)

### Adding Translations

```json
// messages/en.json
{
  "common": {
    "save": "Save",
    "cancel": "Cancel",
    "delete": "Delete"
  },
  "chat": {
    "placeholder": "Type your message...",
    "send": "Send"
  }
}
```

```json
// messages/th.json
{
  "common": {
    "save": "บันทึก",
    "cancel": "ยกเลิก",
    "delete": "ลบ"
  },
  "chat": {
    "placeholder": "พิมพ์ข้อความ...",
    "send": "ส่ง"
  }
}
```

### Usage in Components

```svelte
<script lang="ts">
  import * as m from '$lib/paraglide/messages';
</script>

<Button>{m.common_save()}</Button>
```

---

## RAG Specific Components

### Markdown & Math Rendering

Since this is a scientific RAG application, responses will contain Markdown and LaTeX.

| Library | Purpose |
|---------|---------|
| `svelte-exmarkdown` | Markdown rendering (Svelte 5 compatible) |
| `katex` | LaTeX math equation rendering |
| `shiki` | Syntax highlighting for code blocks |

```svelte
<script lang="ts">
  import Markdown from 'svelte-exmarkdown';
  import { gfmPlugin } from 'svelte-exmarkdown/gfm';
  import { mathPlugin } from './plugins/math'; // KaTeX integration

  let { content } = $props<{ content: string }>();

  const plugins = [gfmPlugin(), mathPlugin()];
</script>

<Markdown md={content} {plugins} />
```

### Chat Stream Handling

For RAG responses, **NEVER** wait for the full response. Use **Server-Sent Events (SSE)** or **ReadableStream**.

```svelte
<script lang="ts">
  let messages = $state<Message[]>([]);
  let currentResponse = $state('');
  let isStreaming = $state(false);

  async function handleChatSubmit(userMessage: string) {
    // Add user message
    messages.push({ role: 'user', content: userMessage });
    isStreaming = true;
    currentResponse = '';

    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: userMessage }),
    });

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) return;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      currentResponse += decoder.decode(value, { stream: true });
    }

    // Finalize message
    messages.push({ role: 'assistant', content: currentResponse });
    currentResponse = '';
    isStreaming = false;
  }
</script>
```

---

## API Integration

### Backend Connection

- Base URL: `http://localhost:8000` (development)
- Authentication: JWT Bearer token

### API Client Pattern

```typescript
// src/lib/api/client.ts
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const token = getStoredToken(); // from auth store

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options?.headers,
    },
  });

  if (!response.ok) {
    throw new ApiError(response.status, await response.text());
  }

  return response.json();
}

// Usage
export const api = {
  auth: {
    login: (data: LoginInput) => fetchApi<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  },
  projects: {
    list: () => fetchApi<Project[]>('/projects'),
    get: (id: string) => fetchApi<Project>(`/projects/${id}`),
  },
};
```

### Streaming API Client

For chat and RAG endpoints that stream responses:

```typescript
// src/lib/api/stream.ts
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function fetchStream(
  endpoint: string,
  options: RequestInit,
  onChunk: (chunk: string) => void
): Promise<void> {
  const token = getStoredToken();

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options?.headers,
    },
  });

  if (!response.ok) {
    throw new ApiError(response.status, await response.text());
  }

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  if (!reader) {
    throw new Error('Response body is not readable');
  }

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    onChunk(decoder.decode(value, { stream: true }));
  }
}

// Usage
await fetchStream(
  '/chat/completions',
  { method: 'POST', body: JSON.stringify({ message: 'Hello' }) },
  (chunk) => {
    currentMessage += chunk;
  }
);
```

### Type Generation from Backend

Use `openapi-typescript` to generate TypeScript types from FastAPI's OpenAPI schema:

```bash
# Generate types from backend OpenAPI schema
npx openapi-typescript http://localhost:8000/openapi.json -o src/lib/types/api.d.ts
```

Add to `package.json` scripts:

```json
{
  "scripts": {
    "generate:types": "openapi-typescript http://localhost:8000/openapi.json -o src/lib/types/api.d.ts"
  }
}
```

### Polling Pattern for Long-Running Tasks

For tasks like fine-tuning jobs that take time to complete, implement polling with exponential backoff:

```typescript
// src/lib/stores/jobStatus.ts
import { writable } from 'svelte/store';

interface JobState {
  id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress?: number;
  result?: unknown;
  error?: string;
}

export function createJobPoller(jobId: string) {
  const store = writable<JobState>({
    id: jobId,
    status: 'pending',
  });

  let timeoutId: ReturnType<typeof setTimeout>;
  let attempt = 0;
  const maxAttempts = 100;
  const baseDelay = 1000; // 1 second
  const maxDelay = 30000; // 30 seconds

  async function poll() {
    try {
      const response = await fetchApi<JobState>(`/finetune/jobs/${jobId}`);
      store.set(response);

      if (response.status === 'completed' || response.status === 'failed') {
        return; // Stop polling
      }

      // Exponential backoff: 1s, 2s, 4s, 8s... max 30s
      const delay = Math.min(baseDelay * Math.pow(2, attempt), maxDelay);
      attempt++;

      if (attempt < maxAttempts) {
        timeoutId = setTimeout(poll, delay);
      }
    } catch (error) {
      store.update((s) => ({ ...s, status: 'failed', error: String(error) }));
    }
  }

  function start() {
    attempt = 0;
    poll();
  }

  function stop() {
    clearTimeout(timeoutId);
  }

  return {
    subscribe: store.subscribe,
    start,
    stop,
  };
}
```

Usage in component:

```svelte
<script lang="ts">
  import { createJobPoller } from '$lib/stores/jobStatus';
  import { onDestroy } from 'svelte';

  let { jobId } = $props<{ jobId: string }>();

  const poller = createJobPoller(jobId);
  poller.start();

  onDestroy(() => poller.stop());
</script>

{#if $poller.status === 'running'}
  <ProgressBar value={$poller.progress} />
{:else if $poller.status === 'completed'}
  <SuccessMessage result={$poller.result} />
{:else if $poller.status === 'failed'}
  <ErrorMessage error={$poller.error} />
{/if}
```

---

## Commands

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type check
npm run check

# Lint code
npm run lint

# Format code
npm run format

# Add shadcn component
npx shadcn-svelte@latest add [component-name]
```

---

## Environment Variables

Create `.env` file:

```bash
# API
VITE_API_URL=http://localhost:8000

# Feature flags (optional)
VITE_ENABLE_ANALYTICS=false

# All client-exposed variables MUST start with VITE_
```

---

## MCP Tools Available

When working on Svelte code, use these tools:

| Tool | When to Use |
|------|-------------|
| `list-sections` | First, to discover available documentation |
| `get-documentation` | Fetch docs for specific Svelte/SvelteKit topics |
| `svelte-autofixer` | Before finalizing any Svelte code |
| `playground-link` | Only after user requests (never for project files) |

---

## Testing

```bash
# Run tests
npm run test

# Run tests with coverage
npm run test:coverage
```

### Test Location

- Unit tests: `src/lib/**/*.test.ts`
- Component tests: `src/lib/components/**/*.test.ts`
- E2E tests: `tests/`
