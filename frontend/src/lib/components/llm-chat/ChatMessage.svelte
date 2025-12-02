<script lang="ts">
	import { User, Bot } from 'lucide-svelte';
	import { cn } from '$lib/utils';
	import { marked } from 'marked';

	interface Props {
		role: 'user' | 'assistant';
		content: string;
		isStreaming?: boolean;
	}

	let { role, content, isStreaming = false }: Props = $props();

	let isUser = $derived(role === 'user');

	// Configure marked for safe rendering
	marked.setOptions({
		breaks: true,
		gfm: true
	});

	// Render markdown to HTML (skip during streaming for performance)
	let renderedContent = $derived(
		isUser ? content : (isStreaming ? content : marked.parse(content, { async: false }) as string)
	);
</script>

<div class={cn('flex gap-3 p-4 min-w-0', isUser ? 'justify-end' : 'justify-start')}>
	{#if !isUser}
		<div
			class="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground"
		>
			<Bot class="size-5" />
		</div>
	{/if}

	<div
		class={cn(
			'max-w-[80%] rounded-2xl px-4 py-2 text-sm overflow-hidden min-w-0',
			isUser ? 'bg-primary text-primary-foreground rounded-br-md' : 'bg-muted rounded-bl-md'
		)}
	>
		{#if isUser}
			<p class="whitespace-pre-wrap break-words overflow-wrap-anywhere">{content}</p>
		{:else if isStreaming}
			<!-- During streaming: show raw text for performance -->
			<p class="whitespace-pre-wrap break-words overflow-wrap-anywhere">{content}</p>
		{:else}
			<!-- After streaming: render markdown -->
			<div class="prose prose-sm dark:prose-invert max-w-none overflow-wrap-anywhere [word-break:break-word]">
				{@html renderedContent}
			</div>
		{/if}
		{#if isStreaming && !isUser}
			<span class="inline-block size-2 animate-pulse rounded-full bg-current ml-1"></span>
		{/if}
	</div>

	{#if isUser}
		<div
			class="flex size-8 shrink-0 items-center justify-center rounded-full bg-secondary text-secondary-foreground"
		>
			<User class="size-5" />
		</div>
	{/if}
</div>

<style>
	/* Markdown content styles */
	.prose :global(p) {
		margin-bottom: 0.5rem;
	}
	.prose :global(p:last-child) {
		margin-bottom: 0;
	}
	.prose :global(ul),
	.prose :global(ol) {
		margin: 0.5rem 0;
		padding-left: 1.5rem;
	}
	.prose :global(li) {
		margin: 0.25rem 0;
	}
	.prose :global(code) {
		background-color: hsl(var(--muted));
		padding: 0.125rem 0.25rem;
		border-radius: 0.25rem;
		font-size: 0.875em;
	}
	.prose :global(pre) {
		background-color: hsl(var(--muted));
		padding: 0.75rem;
		border-radius: 0.5rem;
		overflow-x: auto;
		margin: 0.5rem 0;
	}
	.prose :global(pre code) {
		background: none;
		padding: 0;
	}
	.prose :global(strong) {
		font-weight: 600;
	}
	.prose :global(h1),
	.prose :global(h2),
	.prose :global(h3),
	.prose :global(h4) {
		font-weight: 600;
		margin: 0.75rem 0 0.5rem 0;
	}
	.prose :global(blockquote) {
		border-left: 3px solid hsl(var(--border));
		padding-left: 0.75rem;
		margin: 0.5rem 0;
		color: hsl(var(--muted-foreground));
	}
</style>
