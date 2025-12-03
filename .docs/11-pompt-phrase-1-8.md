# Phase 1.8: Chat Enhancements

## Overview

ปรับปรุง Chat UI ให้มี UX ดีขึ้น - timestamps, copy, regenerate, syntax highlighting, auto-title, system prompt

---

## [x] Task 1: Message Timestamps

**Prompt:**
```
Add message timestamps to chat UI.

Requirements:
- Display time (HH:MM) for each message in ChatMessage component
- Show below message content, right-aligned, small muted text
- Don't show for streaming messages
- Format: Thai locale or 24-hour format

Files: ChatMessage.svelte, LLMChat.svelte
Note: Message already has createdAt field, just need to display it
```

---

## [x] Task 2: Copy Button

**Prompt:**
```
Add copy button to each chat message.

Requirements:
- Show copy icon button on message hover (top-right corner)
- Click copies message content to clipboard
- Show checkmark icon for 2 seconds after copying
- Works for both user and assistant messages

Files: ChatMessage.svelte
Icons: Copy, Check from lucide-svelte
```

---

## [x] Task 3: Code Syntax Highlighting

**Prompt:**
```
Add syntax highlighting for code blocks in assistant messages.

Requirements:
- Use highlight.js (already installed v11.11.1, not used yet)
- Highlight code blocks rendered by marked
- Support common languages: javascript, typescript, python, bash, json, etc.
- Use github-dark or similar theme that works with dark/light mode
- marked v17 may need marked-highlight package for integration

Files: ChatMessage.svelte
Check: How marked v17 integrates with highlight.js
```

---

## [x] Task 4: Auto-generate Conversation Title

**Prompt:**
```
Auto-generate conversation title from first user message.

Requirements:
- When creating new conversation, use first user message as title
- Truncate to ~50 chars, end with "..." if longer
- Set title after first message is saved (in chat stream endpoint)
- Don't override if title already exists

Files:
- Backend: chat.py, conversation.py (service)
- No frontend changes needed (title already displayed in sidebar)
```

---

## Task 5: Regenerate Response Button

**Prompt:**
```
Add regenerate button for last assistant response.

Requirements:
- Show refresh icon button on last assistant message only
- Click removes last assistant message and resends last user message
- Handle state: remove message from UI, call chat API again
- Don't duplicate user message in DB (need skip_save flag or delete+resend)
- Disable during streaming

Files: ChatMessage.svelte, LLMChat.svelte
Consider: May need backend endpoint to delete last message, or handle in frontend state only
```

---

## Task 6: System Prompt per Conversation

**Prompt:**
```
Add system prompt/instruction field per conversation.

Requirements:
- Add system_prompt column to Conversation model (nullable text)
- Create alembic migration
- Update conversation schemas (create/update)
- Update chat endpoint to prepend system message if conversation has system_prompt
- Add UI: button in ChatHeader to open dialog for editing system prompt
- Save system prompt via PATCH /api/conversations/{id}

Files:
- Backend: conversation model, schemas, migration, chat.py
- Frontend: ChatHeader.svelte (add dialog), conversations.ts (update API)

This is the most complex task - needs DB migration + full-stack changes.
```

---

## Implementation Order

| Order | Task | Difficulty | Scope |
|-------|------|------------|-------|
| 1 | Timestamps | Easy | Frontend only |
| 2 | Copy Button | Easy | Frontend only |
| 3 | Syntax Highlighting | Medium | Frontend + package |
| 4 | Auto Title | Medium | Backend |
| 5 | Regenerate | Medium | Frontend + state |
| 6 | System Prompt | Hard | Full-stack + migration |

---

## Key Files Reference

**Frontend:**
- `frontend/src/lib/components/llm-chat/ChatMessage.svelte` - message display
- `frontend/src/lib/components/llm-chat/LLMChat.svelte` - main chat, state management
- `frontend/src/lib/components/llm-chat/ChatHeader.svelte` - header with settings
- `frontend/src/lib/api/conversations.ts` - conversation API client

**Backend:**
- `backend/app/routes/chat.py` - POST /chat, POST /chat/stream
- `backend/app/services/conversation.py` - conversation CRUD
- `backend/app/models/conversation.py` - Conversation model
- `backend/app/schemas/conversation.py` - Pydantic schemas

**Already Installed:**
- highlight.js v11.11.1
- marked v17.0.1
- lucide-svelte (icons)
