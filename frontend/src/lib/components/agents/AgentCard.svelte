<script lang="ts">
	import * as Card from '$lib/components/ui/card';
	import { Badge } from '$lib/components/ui/badge';
	import { Button } from '$lib/components/ui/button';
	import { Pencil, Trash2 } from 'lucide-svelte';
	import type { AgentInfo } from '$lib/api';

	interface Props {
		agent: AgentInfo;
		selected?: boolean;
		onclick?: () => void;
		onEdit?: () => void;
		onDelete?: () => void;
	}

	let { agent, selected = false, onclick, onEdit, onDelete }: Props = $props();

	let isUserAgent = $derived(agent.source === 'user');

	function getAgentIcon(icon?: string): string {
		if (!icon) return '🤖';
		const iconMap: Record<string, string> = {
			search: '🔍',
			calculator: '🔢',
			code: '💻',
			write: '✍️',
			chart: '📊',
			brain: '🧠',
			robot: '🤖',
			sparkles: '✨',
		};
		return iconMap[icon] || '🤖';
	}
</script>

<div class="w-full h-full">
	<Card.Root
		class="h-full flex flex-col transition-all hover:shadow-md {selected
			? 'ring-2 ring-primary border-primary'
			: 'hover:border-muted-foreground/50'}"
	>
		<Card.Header class="pb-3">
			<div class="flex items-center justify-between">
				<button type="button" class="flex items-center gap-3 text-left cursor-pointer flex-1" onclick={onclick}>
					<span class="text-2xl">{getAgentIcon(agent.icon)}</span>
					<Card.Title class="text-base">{agent.name}</Card.Title>
				</button>
				<div class="flex items-center gap-1">
					{#if !isUserAgent}
						<Badge variant="outline" class="text-xs">System</Badge>
					{/if}
					{#if isUserAgent && onEdit}
						<Button
							variant="ghost"
							size="icon"
							class="size-8"
							onclick={(e) => { e.stopPropagation(); onEdit?.(); }}
						>
							<Pencil class="size-4" />
						</Button>
					{/if}
					{#if isUserAgent && onDelete}
						<Button
							variant="ghost"
							size="icon"
							class="size-8 text-destructive hover:text-destructive"
							onclick={(e) => { e.stopPropagation(); onDelete?.(); }}
						>
							<Trash2 class="size-4" />
						</Button>
					{/if}
				</div>
			</div>
		</Card.Header>
		<Card.Content class="pt-0 flex-1 flex flex-col">
			<button type="button" class="text-left cursor-pointer flex-1 flex flex-col" onclick={onclick}>
				<p class="text-sm text-muted-foreground mb-3 line-clamp-2 min-h-[2.5rem]">
					{agent.description || ''}
				</p>
				<div class="flex flex-wrap gap-1.5 mt-auto">
					{#if agent.tools && agent.tools.length > 0}
						{#each agent.tools as tool}
							<Badge variant="secondary" class="text-xs">
								{tool}
							</Badge>
						{/each}
					{/if}
				</div>
			</button>
		</Card.Content>
	</Card.Root>
</div>
