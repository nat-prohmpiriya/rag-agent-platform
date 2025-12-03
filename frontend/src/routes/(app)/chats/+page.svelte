<script lang="ts">
	import { MessageSquare, Search, Trash2 } from 'lucide-svelte';
	import { Input } from '$lib/components/ui/input';
	import { Button } from '$lib/components/ui/button';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { conversationsApi, type Conversation } from '$lib/api';

	let conversations = $state<Conversation[]>([]);
	let loading = $state(true);
	let searchQuery = $state('');

	let filteredConversations = $derived(
		searchQuery
			? conversations.filter((c) =>
					(c.title ?? '').toLowerCase().includes(searchQuery.toLowerCase())
				)
			: conversations
	);

	onMount(async () => {
		await loadConversations();
	});

	async function loadConversations() {
		try {
			const response = await conversationsApi.list(1, 100);
			conversations = response.items;
		} catch (e) {
			console.error('Failed to load conversations:', e);
		} finally {
			loading = false;
		}
	}

	async function handleDelete(id: string, event: MouseEvent) {
		event.stopPropagation();
		try {
			await conversationsApi.delete(id);
			conversations = conversations.filter((c) => c.id !== id);
		} catch (e) {
			console.error('Failed to delete conversation:', e);
		}
	}

	function handleClick(id: string) {
		goto(`/chat/${id}`);
	}

	function formatDate(dateString: string): string {
		const date = new Date(dateString);
		const now = new Date();
		const diff = now.getTime() - date.getTime();
		const days = Math.floor(diff / (1000 * 60 * 60 * 24));

		if (days === 0) return 'Today';
		if (days === 1) return 'Yesterday';
		if (days < 7) return `${days} days ago`;
		return date.toLocaleDateString();
	}
</script>

<svelte:head>
	<title>Chats | RAG Agent</title>
</svelte:head>

<div class="flex h-full flex-col">
	<!-- Header -->
	<div class="border-b bg-background p-4">
		<div class="flex items-center justify-between">
			<div class="flex items-center gap-2">
				<MessageSquare class="size-5" />
				<h1 class="text-lg font-semibold">Chats</h1>
				{#if conversations.length > 0}
					<span class="text-sm text-muted-foreground">({conversations.length})</span>
				{/if}
			</div>
		</div>

		<!-- Search -->
		<div class="mt-4 relative">
			<Search class="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
			<Input
				type="search"
				placeholder="Search conversations..."
				class="pl-9"
				bind:value={searchQuery}
			/>
		</div>
	</div>

	<!-- Content -->
	<div class="flex-1 overflow-auto p-4">
		<div class="mx-auto max-w-3xl space-y-2">
			{#if loading}
				<div class="flex items-center justify-center py-12">
					<div
						class="size-8 animate-spin rounded-full border-4 border-muted border-t-primary"
					></div>
				</div>
			{:else if filteredConversations.length === 0}
				<div class="rounded-lg border border-dashed flex flex-col items-center p-12">
					<MessageSquare class="size-12 text-muted-foreground/50" />
					<h3 class="mt-4 text-lg font-medium">No conversations</h3>
					<p class="mt-1 text-sm text-muted-foreground">
						{#if searchQuery}
							No conversations matching "{searchQuery}". Try a different search.
						{:else}
							Start a new chat to begin a conversation.
						{/if}
					</p>
					<Button class="mt-4" href="/chat">Start New Chat</Button>
				</div>
			{:else}
				{#each filteredConversations as conversation (conversation.id)}
					<button
						class="w-full flex items-center justify-between rounded-lg border p-4 text-left hover:bg-accent transition-colors group"
						onclick={() => handleClick(conversation.id)}
					>
						<div class="flex-1 min-w-0">
							<h3 class="font-medium truncate">{conversation.title}</h3>
							<p class="text-sm text-muted-foreground">
								{formatDate(conversation.updated_at)}
							</p>
						</div>
						<Button
							variant="ghost"
							size="icon"
							class="opacity-0 group-hover:opacity-100 transition-opacity"
							onclick={(e) => handleDelete(conversation.id, e)}
						>
							<Trash2 class="size-4 text-destructive" />
						</Button>
					</button>
				{/each}
			{/if}
		</div>
	</div>
</div>
