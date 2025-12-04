# Phase 7 Tasks - Debug Panel & User Usage

## Overview

เอกสารนี้เป็น prompt สำหรับ AI (Claude Code) ในการ implement features
แบ่งเป็น 5 tasks ย่อยๆ ที่ทำแยกกันได้

---

## Task 1: Debug Panel Component (Frontend)

```
[ ] Create Debug Panel Component for Chat Messages

LOCATION:
- CREATE: frontend/src/lib/components/llm-chat2/DebugPanel.svelte
- MODIFY: frontend/src/lib/components/llm-chat2/ChatMessage.svelte

EXISTING DATA (already available):
- sources: SourceInfo[] - already in ChatMessage props
  - document_id, filename, chunk_index, score (similarity), content
- ModelInfo has input_price, output_price (per million tokens)

IMPLEMENTATION:

1. Create DebugPanel.svelte:
   - Collapsible panel (default: collapsed)
   - Sections to display:
     a) RAG Info (if sources exist):
        - Chunks retrieved: {sources.length}
        - Sources list: filename, score (formatted as percentage)
        - Expandable chunk content preview
     b) Token Usage (if usage exists):
        - Prompt tokens: {usage.prompt_tokens}
        - Completion tokens: {usage.completion_tokens}
        - Total: {usage.total_tokens}
     c) Cost Estimation:
        - Calculate: (prompt_tokens * input_price + completion_tokens * output_price) / 1_000_000
        - Display as: ~$0.0012
     d) Latency (if available):
        - Retrieval: {retrieval_ms}ms
        - LLM: {llm_ms}ms

2. Update ChatMessage.svelte:
   - Add new optional props: usage?, latency?
   - Add "Debug" toggle button in action buttons row (line 185-226)
   - Icon: Bug from lucide-svelte
   - Only show for assistant messages (not user messages)
   - Render DebugPanel below message when toggled

TYPESCRIPT INTERFACES:

// DebugPanel.svelte props
interface DebugPanelProps {
  sources?: SourceInfo[];
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  latency?: {
    retrieval_ms?: number;
    llm_ms?: number;
  };
  modelPrice?: {
    input: number;   // per million tokens
    output: number;  // per million tokens
  };
}

STYLING:
- Svelte 5 runes: $state() for collapsed toggle
- Use shadcn-svelte Collapsible component
- Monospace font (font-mono) for numbers
- Muted background (bg-muted/50)
- Small text (text-xs)
- Grid layout for stats (grid-cols-2 or grid-cols-3)

MOCK DATA (use until backend ready):
const mockUsage = {
  prompt_tokens: 1250,
  completion_tokens: 456,
  total_tokens: 1706
};
const mockLatency = {
  retrieval_ms: 45,
  llm_ms: 1200
};

VERIFICATION:
1. Run `npm run check` - no TypeScript errors
2. Navigate to /chat, send a message
3. See "Debug" button on assistant message (hover to show)
4. Click button - panel should expand/collapse
5. If RAG enabled, should show sources with scores
6. Mock usage/latency data should display
```

---

## [x] Task 2: Chat API Stream Usage Data (Frontend)

```
[ ] Update Chat API to Handle Usage Data from Stream

LOCATION:
- MODIFY: frontend/src/lib/api/chat.ts
- MODIFY: frontend/src/lib/components/llm-chat2/LLMChat2.svelte

IMPLEMENTATION:

1. Update chat.ts stream() function:
   - Update onDone callback to receive usage and latency data
   - Parse from done event: { done: true, usage: {...}, latency: {...} }

2. Update types in chat.ts:

// Add to existing types
export interface StreamDoneData {
  conversation_id: string;
  sources?: SourceInfo[];
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  latency?: {
    retrieval_ms?: number;
    llm_ms?: number;
  };
}

// Update stream function signature
export async function stream(
  request: ChatRequest,
  onChunk: (content: string) => void,
  onDone: (data: StreamDoneData) => void,  // CHANGED
  onError: (error: string) => void,
  signal?: AbortSignal
): Promise<void>

3. Update LLMChat2.svelte:

// Update Message interface
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  createdAt: Date;
  sources?: SourceInfo[];
  usage?: { prompt_tokens: number; completion_tokens: number; total_tokens: number };
  latency?: { retrieval_ms?: number; llm_ms?: number };
}

// Update handleSend() onDone callback (around line 134):
(doneData) => {
  const assistantMessage: Message = {
    id: crypto.randomUUID(),
    role: 'assistant',
    content: streamingContent,
    createdAt: new Date(),
    sources: doneData.sources,
    usage: doneData.usage,      // ADD
    latency: doneData.latency   // ADD
  };
  // ... rest of code
}

// Pass to ChatMessage component (around line 349):
<ChatMessage
  role={message.role}
  content={message.content}
  sources={message.sources}
  usage={message.usage}        // ADD
  latency={message.latency}    // ADD
  ...
/>

VERIFICATION:
1. Run `npm run check` - no TypeScript errors
2. Send chat message
3. Check browser console - no errors parsing stream
4. Debug panel should receive data (when backend ready)
```

---

## [x] Task 3: Backend - Add Usage & Latency to Stream Response

```
[ ] Add Usage and Latency Data to Chat Streaming Response

LOCATION:
- MODIFY: backend/app/routes/chat.py

EXISTING CODE (line 434-490 in chat_stream function):
- event_generator() yields SSE chunks
- Done event at line 467-475 only sends: content, done, conversation_id, sources

IMPLEMENTATION:

1. Add timing imports at top of file:
import time

2. Add latency tracking before RAG retrieval (around line 406):
retrieval_start = time.time()
# ... existing RAG code ...
retrieval_latency_ms = int((time.time() - retrieval_start) * 1000) if data.use_rag else None

3. Track LLM latency in event_generator (around line 434):
async def event_generator():
    full_response = ""
    llm_start = time.time()
    try:
        async for chunk in llm_client.chat_completion_stream(...):
            # ... existing code ...

        llm_latency_ms = int((time.time() - llm_start) * 1000)

        # ... save message code ...

4. Update done event to include usage and latency (line 467-475):
# Send done signal with all data
done_data = {
    "content": "",
    "done": True,
    "conversation_id": str(conversation_id),
}
if sources_data:
    done_data["sources"] = sources_data

# Add usage (estimate from response length, or get from LiteLLM if available)
# Note: Streaming doesn't return usage, so we estimate or skip
done_data["latency"] = {
    "retrieval_ms": retrieval_latency_ms,
    "llm_ms": llm_latency_ms
}

yield f"data: {json.dumps(done_data)}\n\n"

5. For non-streaming endpoint, usage is already available from LLM response.
   Make sure it's included in the response.

PYDANTIC SCHEMA (add to schemas/chat.py if needed):

class LatencyInfo(BaseModel):
    retrieval_ms: int | None = None
    llm_ms: int | None = None

VERIFICATION:
1. Run `uv run ruff check backend/` - no lint errors
2. Start backend: `uv run uvicorn app.main:app --reload`
3. Send streaming chat request
4. Check SSE done event includes latency data
5. Test with RAG enabled - should include retrieval_ms
```

---

## [x] Task 4: User Usage Tab Component (Frontend)

```
[ ] Create User Usage Tab in Profile Page

LOCATION:
- CREATE: frontend/src/lib/components/profile/UsageTab.svelte
- MODIFY: frontend/src/routes/(app)/profile/+page.svelte
- MODIFY: frontend/src/lib/api/profile.ts

EXISTING CODE:
- Profile page at frontend/src/routes/(app)/profile/+page.svelte
- Has UserStats (conversations_count, documents_count, agents_count, total_messages)
- Stats shown in card at line 165-206

IMPLEMENTATION:

1. Add to frontend/src/lib/api/profile.ts:

export interface UserUsage {
  total_tokens: number;
  total_messages: number;
  tokens_this_month: number;
  messages_this_month: number;
  estimated_cost: number;
  cost_this_month: number;
  quota?: {
    tokens_limit: number;
    tokens_used: number;
    percentage: number;
  };
}

// Mock function until backend ready
export async function getUsage(): Promise<UserUsage> {
  // TODO: Replace with actual API call when backend ready
  // return await fetchApi<UserUsage>('/api/profile/usage');

  // Mock data for now
  return {
    total_tokens: 125000,
    total_messages: 450,
    tokens_this_month: 45000,
    messages_this_month: 120,
    estimated_cost: 2.34,
    cost_this_month: 0.89,
    quota: {
      tokens_limit: 100000,
      tokens_used: 45000,
      percentage: 45
    }
  };
}

2. Create UsageTab.svelte:

Props:
interface Props {
  usage: UserUsage | null;
  stats: UserStats | null;
  loading: boolean;
}

Sections to display:
- Token Usage Card:
  - This month: {tokens_this_month.toLocaleString()} tokens
  - Progress bar if quota exists (percentage)
  - All time: {total_tokens.toLocaleString()} tokens

- Cost Card:
  - This month: ${cost_this_month.toFixed(2)}
  - Total: ${estimated_cost.toFixed(2)}

- Activity Card:
  - Messages: {messages_this_month} this month / {total_messages} total
  - Conversations: {stats.conversations_count}
  - Documents: {stats.documents_count}
  - Agents: {stats.agents_count}

3. Update Profile page to use Tabs:

Import shadcn Tabs:
import * as Tabs from '$lib/components/ui/tabs';

Add usage state and load function:
let usage = $state<UserUsage | null>(null);

async function loadData() {
  // ... existing code ...
  const [profileData, statsData, usageData] = await Promise.all([
    profileApi.getProfile(),
    profileApi.getStats(),
    profileApi.getUsage()
  ]);
  // ...
  usage = usageData;
}

Wrap content with Tabs (replace line 106 onwards):
<Tabs.Root value="profile" class="w-full">
  <Tabs.List class="mb-6">
    <Tabs.Trigger value="profile">Profile</Tabs.Trigger>
    <Tabs.Trigger value="usage">Usage</Tabs.Trigger>
  </Tabs.List>

  <Tabs.Content value="profile">
    <!-- Move existing User Info + Account Management cards here -->
  </Tabs.Content>

  <Tabs.Content value="usage">
    <UsageTab {usage} {stats} {loading} />
  </Tabs.Content>
</Tabs.Root>

STYLING:
- Use existing Card components from profile page
- Progress component from shadcn-svelte
- Icons: Coins, Zap, TrendingUp, Activity from lucide-svelte
- Format numbers with toLocaleString()
- Format currency with toFixed(2)

VERIFICATION:
1. Run `npm run check` - no TypeScript errors
2. Navigate to /profile
3. Should see 2 tabs: "Profile" and "Usage"
4. Click "Usage" tab
5. Should show token stats, cost, progress bar with mock data
6. Loading state should show spinner
```

---

## [x] Task 5: Backend - User Usage API Endpoint

```
[ ] Create GET /api/profile/usage Endpoint

LOCATION:
- MODIFY: backend/app/routes/profile.py
- MODIFY: backend/app/schemas/profile.py (or create)

EXISTING CODE:
- Profile routes at backend/app/routes/profile.py
- Message model has tokens_used field
- User model has tier field

IMPLEMENTATION:

1. Add schema (backend/app/schemas/profile.py or add to existing):

from pydantic import BaseModel

class UsageQuota(BaseModel):
    tokens_limit: int
    tokens_used: int
    percentage: int

class UserUsageResponse(BaseModel):
    total_tokens: int
    total_messages: int
    tokens_this_month: int
    messages_this_month: int
    estimated_cost: float
    cost_this_month: float
    quota: UsageQuota | None = None

2. Add route to profile.py:

from datetime import datetime
from sqlalchemy import func, select, and_
from app.models.message import Message
from app.models.conversation import Conversation

# Token limits by tier (can move to config)
TIER_LIMITS = {
    "free": 50000,
    "basic": 200000,
    "pro": 1000000,
    "enterprise": None  # unlimited
}

# Cost per token (simplified, can be more complex per model)
COST_PER_1M_TOKENS = 0.50  # $0.50 per million tokens average

@router.get("/usage")
async def get_usage(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[UserUsageResponse]:
    """Get user's token usage statistics."""
    ctx = get_context()

    # Get current month start
    now = datetime.utcnow()
    month_start = datetime(now.year, now.month, 1)

    # Get user's conversation IDs
    conv_stmt = select(Conversation.id).where(
        Conversation.user_id == current_user.id
    )
    conv_result = await db.execute(conv_stmt)
    conv_ids = [row[0] for row in conv_result.all()]

    if not conv_ids:
        # No conversations, return zeros
        return BaseResponse(
            trace_id=ctx.trace_id,
            data=UserUsageResponse(
                total_tokens=0,
                total_messages=0,
                tokens_this_month=0,
                messages_this_month=0,
                estimated_cost=0.0,
                cost_this_month=0.0,
                quota=None
            )
        )

    # Total tokens and messages (all time)
    total_stmt = select(
        func.coalesce(func.sum(Message.tokens_used), 0).label("total_tokens"),
        func.count(Message.id).label("total_messages")
    ).where(Message.conversation_id.in_(conv_ids))

    total_result = await db.execute(total_stmt)
    total_row = total_result.one()
    total_tokens = int(total_row.total_tokens)
    total_messages = int(total_row.total_messages)

    # This month tokens and messages
    month_stmt = select(
        func.coalesce(func.sum(Message.tokens_used), 0).label("tokens"),
        func.count(Message.id).label("messages")
    ).where(
        and_(
            Message.conversation_id.in_(conv_ids),
            Message.created_at >= month_start
        )
    )

    month_result = await db.execute(month_stmt)
    month_row = month_result.one()
    tokens_this_month = int(month_row.tokens)
    messages_this_month = int(month_row.messages)

    # Calculate costs
    estimated_cost = (total_tokens / 1_000_000) * COST_PER_1M_TOKENS
    cost_this_month = (tokens_this_month / 1_000_000) * COST_PER_1M_TOKENS

    # Get quota based on tier
    quota = None
    tier_limit = TIER_LIMITS.get(current_user.tier)
    if tier_limit:
        percentage = min(100, int((tokens_this_month / tier_limit) * 100))
        quota = UsageQuota(
            tokens_limit=tier_limit,
            tokens_used=tokens_this_month,
            percentage=percentage
        )

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=UserUsageResponse(
            total_tokens=total_tokens,
            total_messages=total_messages,
            tokens_this_month=tokens_this_month,
            messages_this_month=messages_this_month,
            estimated_cost=round(estimated_cost, 2),
            cost_this_month=round(cost_this_month, 2),
            quota=quota
        )
    )

VERIFICATION:
1. Run `uv run ruff check backend/` - no lint errors
2. Start backend: `uv run uvicorn app.main:app --reload`
3. Call API: GET /api/profile/usage with auth token
4. Should return usage data with correct totals
5. Test with user that has messages with tokens_used
6. Verify quota calculation based on user tier
```

---

## Files Summary

### Frontend Files:
| Task | Action | File |
|------|--------|------|
| 1 | CREATE | `frontend/src/lib/components/llm-chat2/DebugPanel.svelte` |
| 1 | MODIFY | `frontend/src/lib/components/llm-chat2/ChatMessage.svelte` |
| 2 | MODIFY | `frontend/src/lib/api/chat.ts` |
| 2 | MODIFY | `frontend/src/lib/components/llm-chat2/LLMChat2.svelte` |
| 4 | CREATE | `frontend/src/lib/components/profile/UsageTab.svelte` |
| 4 | MODIFY | `frontend/src/routes/(app)/profile/+page.svelte` |
| 4 | MODIFY | `frontend/src/lib/api/profile.ts` |

### Backend Files:
| Task | Action | File |
|------|--------|------|
| 3 | MODIFY | `backend/app/routes/chat.py` |
| 5 | MODIFY | `backend/app/routes/profile.py` |
| 5 | MODIFY | `backend/app/schemas/profile.py` |

---

## Task Dependencies

```
Task 3 (Backend Stream) ──────► Task 2 (Frontend Stream API) ──────► Task 1 (Debug Panel UI)

Task 5 (Backend Usage API) ──────► Task 4 (Usage Tab UI)
```

## Recommended Order (Backend First):

### Debug Panel Flow:
1. **Task 3** - Backend: Add latency to stream response
2. **Task 2** - Frontend: Update chat API to handle usage/latency
3. **Task 1** - Frontend: Create Debug Panel component

### Usage Tab Flow:
4. **Task 5** - Backend: Create usage API endpoint
5. **Task 4** - Frontend: Create Usage Tab in Profile

---

## Notes

- ทำ Backend ก่อน → Frontend ใช้ data จริงได้เลย ไม่ต้อง mock
- แต่ละ Flow (Debug Panel / Usage Tab) ทำแยกกันได้
- Backend tasks ไม่ต้อง migrate (ไม่มี schema change)
- ทุก Task มี verification steps
