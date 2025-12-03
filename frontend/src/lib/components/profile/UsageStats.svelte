<script lang="ts">
	import * as Card from '$lib/components/ui/card';
	import type { UserStats } from '$lib/api';
	import { MessageSquare, FileText, Bot, MessagesSquare } from 'lucide-svelte';

	let { stats } = $props<{
		stats: UserStats;
	}>();

	const statItems = $derived([
		{
			label: 'Conversations',
			value: stats.conversations_count,
			icon: MessageSquare,
			color: 'text-blue-500'
		},
		{
			label: 'Documents',
			value: stats.documents_count,
			icon: FileText,
			color: 'text-green-500'
		},
		{
			label: 'Custom Agents',
			value: stats.agents_count,
			icon: Bot,
			color: 'text-purple-500'
		},
		{
			label: 'Total Messages',
			value: stats.total_messages,
			icon: MessagesSquare,
			color: 'text-orange-500'
		}
	]);
</script>

<div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
	{#each statItems as item}
		<Card.Root>
			<Card.Content class="pt-6">
				<div class="flex flex-col items-center text-center space-y-2">
					<div class="p-3 rounded-full bg-muted">
						<item.icon class="size-6 {item.color}" />
					</div>
					<div class="text-3xl font-bold">{item.value.toLocaleString()}</div>
					<div class="text-sm text-muted-foreground">{item.label}</div>
				</div>
			</Card.Content>
		</Card.Root>
	{/each}
</div>
