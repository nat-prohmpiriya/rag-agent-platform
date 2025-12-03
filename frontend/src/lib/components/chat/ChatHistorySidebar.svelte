<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { ScrollArea } from '$lib/components/ui/scroll-area';
	import { Separator } from '$lib/components/ui/separator';
	import { Plus, MessageSquare, Trash2, Search, X, Loader2 } from 'lucide-svelte';
	import type { Conversation, ConversationSearchResult } from '$lib/api/conversations';
	import { conversationsApi } from '$lib/api/conversations';

	let {
		conversations,
		currentId = null,
		loading = false,
		onSelect,
		onNew,
		onDelete
	} = $props<{
		conversations: Conversation[];
		currentId?: string | null;
		loading?: boolean;
		onSelect: (id: string) => void;
		onNew: () => void;
		onDelete: (id: string) => void;
	}>();

	// Search state
	let searchQuery = $state('');
	let searchResults = $state<ConversationSearchResult[]>([]);
	let isSearching = $state(false);
	let searchError = $state<string | null>(null);
	let searchTimeout: ReturnType<typeof setTimeout> | null = null;

	// Debounced search
	function handleSearchInput(value: string) {
		searchQuery = value;
		searchError = null;

		if (searchTimeout) {
			clearTimeout(searchTimeout);
		}

		if (!value.trim()) {
			searchResults = [];
			isSearching = false;
			return;
		}

		isSearching = true;
		searchTimeout = setTimeout(async () => {
			try {
				const response = await conversationsApi.search(value.trim());
				searchResults = response.items;
			} catch (e) {
				console.error('Search failed:', e);
				searchError = 'Search failed';
				searchResults = [];
			} finally {
				isSearching = false;
			}
		}, 300);
	}

	function clearSearch() {
		searchQuery = '';
		searchResults = [];
		searchError = null;
	}

	function handleSearchResultClick(conversationId: string) {
		clearSearch();
		onSelect(conversationId);
	}

	// Group conversations by date
	interface GroupedConversations {
		today: Conversation[];
		yesterday: Conversation[];
		previousWeek: Conversation[];
		older: Conversation[];
	}

	function groupConversations(convs: Conversation[]): GroupedConversations {
		const now = new Date();
		const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
		const yesterday = new Date(today);
		yesterday.setDate(yesterday.getDate() - 1);
		const weekAgo = new Date(today);
		weekAgo.setDate(weekAgo.getDate() - 7);

		const result: GroupedConversations = {
			today: [],
			yesterday: [],
			previousWeek: [],
			older: []
		};

		for (const conv of convs) {
			const convDate = new Date(conv.created_at);
			if (convDate >= today) {
				result.today.push(conv);
			} else if (convDate >= yesterday) {
				result.yesterday.push(conv);
			} else if (convDate >= weekAgo) {
				result.previousWeek.push(conv);
			} else {
				result.older.push(conv);
			}
		}

		return result;
	}

	let grouped = $derived(groupConversations(conversations));
	let isSearchMode = $derived(searchQuery.trim().length > 0);

	function getDisplayTitle(conv: Conversation): string {
		if (conv.title) return conv.title;
		if (conv.last_message_preview) {
			return conv.last_message_preview.length > 30
				? conv.last_message_preview.substring(0, 30) + '...'
				: conv.last_message_preview;
		}
		return 'New conversation';
	}

	function handleDelete(e: MouseEvent, id: string) {
		e.preventDefault();
		e.stopPropagation();
		onDelete(id);
	}

	let hoveredId = $state<string | null>(null);
</script>

<aside class="flex h-full w-64 flex-col border-r bg-background">
	<!-- New chat button -->
	<div class="p-4">
		<Button class="w-full" onclick={onNew}>
			<Plus class="mr-2 h-4 w-4" />
			New Chat
		</Button>
	</div>

	<!-- Search input -->
	<div class="px-4 pb-2">
		<div class="relative">
			<Search class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
			<Input
				type="text"
				placeholder="Search conversations..."
				class="pl-9 pr-9"
				value={searchQuery}
				oninput={(e) => handleSearchInput(e.currentTarget.value)}
			/>
			{#if searchQuery}
				<button
					class="absolute right-2 top-1/2 -translate-y-1/2 rounded p-1 text-muted-foreground hover:text-foreground"
					onclick={clearSearch}
				>
					{#if isSearching}
						<Loader2 class="h-4 w-4 animate-spin" />
					{:else}
						<X class="h-4 w-4" />
					{/if}
				</button>
			{/if}
		</div>
	</div>

	<Separator />

	<!-- Search Results or Conversations list -->
	<ScrollArea class="flex-1">
		{#if isSearchMode}
			<!-- Search Results -->
			<div class="p-2">
				{#if isSearching}
					<div class="space-y-2 p-4">
						{#each Array(3) as _}
							<div class="h-16 animate-pulse rounded-lg bg-muted"></div>
						{/each}
					</div>
				{:else if searchError}
					<div class="flex flex-col items-center justify-center p-8 text-center text-muted-foreground">
						<p class="text-sm text-destructive">{searchError}</p>
					</div>
				{:else if searchResults.length === 0}
					<div class="flex flex-col items-center justify-center p-8 text-center text-muted-foreground">
						<Search class="mb-2 h-8 w-8 opacity-50" />
						<p class="text-sm">No results found</p>
						<p class="text-xs">Try different keywords</p>
					</div>
				{:else}
					<p class="mb-2 px-3 text-xs font-medium text-muted-foreground">
						{searchResults.length} result{searchResults.length !== 1 ? 's' : ''} found
					</p>
					{#each searchResults as result}
						<div
							class="group relative mb-2 cursor-pointer rounded-lg border p-3 text-left text-sm transition-colors hover:bg-accent"
							onclick={() => handleSearchResultClick(result.conversation_id)}
							onkeydown={(e) => e.key === 'Enter' && handleSearchResultClick(result.conversation_id)}
							role="button"
							tabindex="0"
						>
							<div class="mb-1 flex items-center gap-2">
								<MessageSquare class="h-4 w-4 shrink-0 text-muted-foreground" />
								<span class="flex-1 truncate font-medium">
									{result.title || 'Untitled conversation'}
								</span>
								<span class="shrink-0 text-xs text-muted-foreground">
									{result.match_count} match{result.match_count !== 1 ? 'es' : ''}
								</span>
							</div>
							<!-- Highlighted snippet with <mark> tags -->
							<p class="line-clamp-2 text-xs text-muted-foreground [&>mark]:bg-yellow-200 [&>mark]:text-foreground dark:[&>mark]:bg-yellow-500/30">
								{@html result.snippet}
							</p>
						</div>
					{/each}
				{/if}
			</div>
		{:else if loading}
			<!-- Loading skeleton -->
			<div class="space-y-2 p-4">
				{#each Array(5) as _}
					<div class="h-10 animate-pulse rounded-lg bg-muted"></div>
				{/each}
			</div>
		{:else if conversations.length === 0}
			<!-- Empty state -->
			<div class="flex flex-col items-center justify-center p-8 text-center text-muted-foreground">
				<MessageSquare class="mb-2 h-8 w-8 opacity-50" />
				<p class="text-sm">No conversations yet</p>
				<p class="text-xs">Start a new chat to begin</p>
			</div>
		{:else}
			<div class="p-2">
				<!-- Today -->
				{#if grouped.today.length > 0}
					<div class="mb-2">
						<p class="mb-1 px-3 text-xs font-medium text-muted-foreground">Today</p>
						{#each grouped.today as conv}
							<div
								class="group relative flex w-full cursor-pointer items-center gap-2 rounded-lg px-3 py-2 text-left text-sm transition-colors hover:bg-accent {currentId === conv.id ? 'bg-accent' : ''}"
								onclick={() => onSelect(conv.id)}
								onkeydown={(e) => e.key === 'Enter' && onSelect(conv.id)}
								onmouseenter={() => (hoveredId = conv.id)}
								onmouseleave={() => (hoveredId = null)}
								role="button"
								tabindex="0"
							>
								<MessageSquare class="h-4 w-4 shrink-0 text-muted-foreground" />
								<span class="flex-1 truncate">{getDisplayTitle(conv)}</span>
								{#if hoveredId === conv.id}
									<button
										class="shrink-0 rounded p-1 text-muted-foreground hover:bg-destructive/10 hover:text-destructive"
										onclick={(e) => handleDelete(e, conv.id)}
									>
										<Trash2 class="h-4 w-4" />
									</button>
								{/if}
							</div>
						{/each}
					</div>
				{/if}

				<!-- Yesterday -->
				{#if grouped.yesterday.length > 0}
					<div class="mb-2">
						<p class="mb-1 px-3 text-xs font-medium text-muted-foreground">Yesterday</p>
						{#each grouped.yesterday as conv}
							<div
								class="group relative flex w-full cursor-pointer items-center gap-2 rounded-lg px-3 py-2 text-left text-sm transition-colors hover:bg-accent {currentId === conv.id ? 'bg-accent' : ''}"
								onclick={() => onSelect(conv.id)}
								onkeydown={(e) => e.key === 'Enter' && onSelect(conv.id)}
								onmouseenter={() => (hoveredId = conv.id)}
								onmouseleave={() => (hoveredId = null)}
								role="button"
								tabindex="0"
							>
								<MessageSquare class="h-4 w-4 shrink-0 text-muted-foreground" />
								<span class="flex-1 truncate">{getDisplayTitle(conv)}</span>
								{#if hoveredId === conv.id}
									<button
										class="shrink-0 rounded p-1 text-muted-foreground hover:bg-destructive/10 hover:text-destructive"
										onclick={(e) => handleDelete(e, conv.id)}
									>
										<Trash2 class="h-4 w-4" />
									</button>
								{/if}
							</div>
						{/each}
					</div>
				{/if}

				<!-- Previous 7 days -->
				{#if grouped.previousWeek.length > 0}
					<div class="mb-2">
						<p class="mb-1 px-3 text-xs font-medium text-muted-foreground">Previous 7 days</p>
						{#each grouped.previousWeek as conv}
							<div
								class="group relative flex w-full cursor-pointer items-center gap-2 rounded-lg px-3 py-2 text-left text-sm transition-colors hover:bg-accent {currentId === conv.id ? 'bg-accent' : ''}"
								onclick={() => onSelect(conv.id)}
								onkeydown={(e) => e.key === 'Enter' && onSelect(conv.id)}
								onmouseenter={() => (hoveredId = conv.id)}
								onmouseleave={() => (hoveredId = null)}
								role="button"
								tabindex="0"
							>
								<MessageSquare class="h-4 w-4 shrink-0 text-muted-foreground" />
								<span class="flex-1 truncate">{getDisplayTitle(conv)}</span>
								{#if hoveredId === conv.id}
									<button
										class="shrink-0 rounded p-1 text-muted-foreground hover:bg-destructive/10 hover:text-destructive"
										onclick={(e) => handleDelete(e, conv.id)}
									>
										<Trash2 class="h-4 w-4" />
									</button>
								{/if}
							</div>
						{/each}
					</div>
				{/if}

				<!-- Older -->
				{#if grouped.older.length > 0}
					<div class="mb-2">
						<p class="mb-1 px-3 text-xs font-medium text-muted-foreground">Older</p>
						{#each grouped.older as conv}
							<div
								class="group relative flex w-full cursor-pointer items-center gap-2 rounded-lg px-3 py-2 text-left text-sm transition-colors hover:bg-accent {currentId === conv.id ? 'bg-accent' : ''}"
								onclick={() => onSelect(conv.id)}
								onkeydown={(e) => e.key === 'Enter' && onSelect(conv.id)}
								onmouseenter={() => (hoveredId = conv.id)}
								onmouseleave={() => (hoveredId = null)}
								role="button"
								tabindex="0"
							>
								<MessageSquare class="h-4 w-4 shrink-0 text-muted-foreground" />
								<span class="flex-1 truncate">{getDisplayTitle(conv)}</span>
								{#if hoveredId === conv.id}
									<button
										class="shrink-0 rounded p-1 text-muted-foreground hover:bg-destructive/10 hover:text-destructive"
										onclick={(e) => handleDelete(e, conv.id)}
									>
										<Trash2 class="h-4 w-4" />
									</button>
								{/if}
							</div>
						{/each}
					</div>
				{/if}
			</div>
		{/if}
	</ScrollArea>
</aside>
