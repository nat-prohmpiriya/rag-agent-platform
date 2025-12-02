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
