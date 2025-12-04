<script lang="ts">
	import * as Card from '$lib/components/ui/card';
	import { Progress } from '$lib/components/ui/progress';
	import { Coins, Zap, TrendingUp, Activity, MessageSquare, FileText, Bot, Loader2 } from 'lucide-svelte';
	import type { UserUsage, UserStats } from '$lib/api/profile';

	interface Props {
		usage: UserUsage | null;
		stats: UserStats | null;
		loading: boolean;
	}

	let { usage, stats, loading }: Props = $props();

	function formatNumber(num: number): string {
		return num.toLocaleString();
	}

	function formatCurrency(amount: number): string {
		return `$${amount.toFixed(2)}`;
	}
</script>

{#if loading}
	<div class="flex items-center justify-center py-12">
		<Loader2 class="size-8 animate-spin text-muted-foreground" />
	</div>
{:else if usage}
	<div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
		<!-- Token Usage Card -->
		<Card.Root>
			<Card.Header class="flex flex-row items-center justify-between space-y-0 pb-2">
				<Card.Title class="text-sm font-medium">Token Usage</Card.Title>
				<Zap class="size-4 text-muted-foreground" />
			</Card.Header>
			<Card.Content>
				<div class="space-y-4">
					<div>
						<div class="flex items-baseline gap-2">
							<span class="text-2xl font-bold">{formatNumber(usage.tokens_this_month)}</span>
							<span class="text-sm text-muted-foreground">tokens this month</span>
						</div>
					</div>

					{#if usage.quota}
						<div class="space-y-2">
							<div class="flex items-center justify-between text-sm">
								<span class="text-muted-foreground">Quota Used</span>
								<span class="font-medium">{usage.quota.percentage}%</span>
							</div>
							<Progress value={usage.quota.percentage} max={100} class="h-2" />
							<div class="flex items-center justify-between text-xs text-muted-foreground">
								<span>{formatNumber(usage.quota.tokens_used)} used</span>
								<span>{formatNumber(usage.quota.tokens_limit)} limit</span>
							</div>
						</div>
					{/if}

					<div class="pt-2 border-t">
						<div class="flex items-center justify-between text-sm">
							<span class="text-muted-foreground">All time</span>
							<span class="font-medium">{formatNumber(usage.total_tokens)} tokens</span>
						</div>
					</div>
				</div>
			</Card.Content>
		</Card.Root>

		<!-- Cost Card -->
		<Card.Root>
			<Card.Header class="flex flex-row items-center justify-between space-y-0 pb-2">
				<Card.Title class="text-sm font-medium">Estimated Cost</Card.Title>
				<Coins class="size-4 text-muted-foreground" />
			</Card.Header>
			<Card.Content>
				<div class="space-y-4">
					<div>
						<div class="flex items-baseline gap-2">
							<span class="text-2xl font-bold">{formatCurrency(usage.cost_this_month)}</span>
							<span class="text-sm text-muted-foreground">this month</span>
						</div>
					</div>

					<div class="pt-2 border-t">
						<div class="flex items-center justify-between text-sm">
							<span class="text-muted-foreground">Total spent</span>
							<span class="font-medium">{formatCurrency(usage.estimated_cost)}</span>
						</div>
					</div>
				</div>
			</Card.Content>
		</Card.Root>

		<!-- Messages Card -->
		<Card.Root>
			<Card.Header class="flex flex-row items-center justify-between space-y-0 pb-2">
				<Card.Title class="text-sm font-medium">Messages</Card.Title>
				<TrendingUp class="size-4 text-muted-foreground" />
			</Card.Header>
			<Card.Content>
				<div class="space-y-4">
					<div>
						<div class="flex items-baseline gap-2">
							<span class="text-2xl font-bold">{formatNumber(usage.messages_this_month)}</span>
							<span class="text-sm text-muted-foreground">this month</span>
						</div>
					</div>

					<div class="pt-2 border-t">
						<div class="flex items-center justify-between text-sm">
							<span class="text-muted-foreground">Total messages</span>
							<span class="font-medium">{formatNumber(usage.total_messages)}</span>
						</div>
					</div>
				</div>
			</Card.Content>
		</Card.Root>

		<!-- Activity Overview Card (spans full width on larger screens) -->
		{#if stats}
			<Card.Root class="md:col-span-2 lg:col-span-3">
				<Card.Header class="flex flex-row items-center justify-between space-y-0 pb-2">
					<Card.Title class="text-sm font-medium">Activity Overview</Card.Title>
					<Activity class="size-4 text-muted-foreground" />
				</Card.Header>
				<Card.Content>
					<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
						<div class="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
							<div class="flex size-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
								<MessageSquare class="size-5 text-primary" />
							</div>
							<div>
								<p class="text-2xl font-bold">{stats.conversations_count}</p>
								<p class="text-xs text-muted-foreground">Conversations</p>
							</div>
						</div>

						<div class="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
							<div class="flex size-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
								<FileText class="size-5 text-primary" />
							</div>
							<div>
								<p class="text-2xl font-bold">{stats.documents_count}</p>
								<p class="text-xs text-muted-foreground">Documents</p>
							</div>
						</div>

						<div class="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
							<div class="flex size-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
								<Bot class="size-5 text-primary" />
							</div>
							<div>
								<p class="text-2xl font-bold">{stats.agents_count}</p>
								<p class="text-xs text-muted-foreground">Custom Agents</p>
							</div>
						</div>

						<div class="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
							<div class="flex size-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
								<MessageSquare class="size-5 text-primary" />
							</div>
							<div>
								<p class="text-2xl font-bold">{stats.total_messages}</p>
								<p class="text-xs text-muted-foreground">Total Messages</p>
							</div>
						</div>
					</div>
				</Card.Content>
			</Card.Root>
		{/if}
	</div>
{:else}
	<Card.Root>
		<Card.Content class="pt-6">
			<p class="text-center text-muted-foreground">No usage data available.</p>
		</Card.Content>
	</Card.Root>
{/if}
