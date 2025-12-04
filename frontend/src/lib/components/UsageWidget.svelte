<script lang="ts">
	import * as Card from '$lib/components/ui/card';
	import * as Alert from '$lib/components/ui/alert';
	import * as Dialog from '$lib/components/ui/dialog';
	import { Progress } from '$lib/components/ui/progress';
	import { Button } from '$lib/components/ui/button';
	import {
		Zap,
		Activity,
		Calendar,
		AlertTriangle,
		XCircle,
		ArrowUpCircle,
		Loader2
	} from 'lucide-svelte';
	import { profileApi, type UserUsage } from '$lib/api/profile';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	interface Props {
		compact?: boolean;
		showAlerts?: boolean;
	}

	let { compact = false, showAlerts = true }: Props = $props();

	let usage: UserUsage | null = $state(null);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let blockedModalOpen = $state(false);

	// Helper to get quota percentage
	function getQuotaPercentage(): number {
		return usage?.quota?.percentage ?? 0;
	}

	// Quota status derived from usage
	let quotaPercentage = $derived(getQuotaPercentage());
	let isWarning = $derived(quotaPercentage >= 80 && quotaPercentage < 95);
	let isCritical = $derived(quotaPercentage >= 95 && quotaPercentage < 100);
	let isBlocked = $derived(quotaPercentage >= 100);

	// Days until reset (assuming monthly reset on 1st)
	function calculateDaysUntilReset(): number {
		const now = new Date();
		const nextMonth = new Date(now.getFullYear(), now.getMonth() + 1, 1);
		const diffTime = nextMonth.getTime() - now.getTime();
		return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
	}
	let daysUntilReset = $derived(calculateDaysUntilReset());

	// Progress bar color based on percentage
	function getProgressColor(): string {
		if (isBlocked) return 'bg-destructive';
		if (isCritical) return 'bg-red-500';
		if (isWarning) return 'bg-yellow-500';
		return 'bg-primary';
	}
	let progressColor = $derived(getProgressColor());

	async function loadUsage() {
		loading = true;
		error = null;
		try {
			usage = await profileApi.getUsage();

			// Auto-show blocked modal if at 100%
			if (showAlerts && usage?.quota?.percentage && usage.quota.percentage >= 100) {
				blockedModalOpen = true;
			}
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load usage data';
		} finally {
			loading = false;
		}
	}

	function formatNumber(num: number): string {
		if (num >= 1000000) {
			return `${(num / 1000000).toFixed(1)}M`;
		}
		if (num >= 1000) {
			return `${(num / 1000).toFixed(1)}K`;
		}
		return num.toLocaleString();
	}

	function handleUpgrade() {
		blockedModalOpen = false;
		goto('/billing');
	}

	onMount(() => {
		loadUsage();
	});
</script>

{#if loading}
	<div class="flex items-center justify-center py-4">
		<Loader2 class="size-5 animate-spin text-muted-foreground" />
	</div>
{:else if error}
	<Alert.Root variant="destructive">
		<AlertTriangle class="size-4" />
		<Alert.Title>Error</Alert.Title>
		<Alert.Description>{error}</Alert.Description>
	</Alert.Root>
{:else if usage}
	<!-- Compact View (for sidebar/header) -->
	{#if compact}
		<div class="space-y-3 p-3">
			<!-- Token Usage -->
			<div class="space-y-1.5">
				<div class="flex items-center justify-between text-xs">
					<span class="flex items-center gap-1.5 text-muted-foreground">
						<Zap class="size-3" />
						Tokens
					</span>
					<span class="font-medium">
						{#if usage.quota}
							{formatNumber(usage.quota.tokens_used)} / {formatNumber(usage.quota.tokens_limit)}
						{:else}
							{formatNumber(usage.tokens_this_month)}
						{/if}
					</span>
				</div>
				{#if usage.quota}
					<div class="relative h-1.5 w-full overflow-hidden rounded-full bg-muted">
						<div
							class="h-full transition-all duration-300 {progressColor}"
							style="width: {Math.min(quotaPercentage, 100)}%"
						></div>
					</div>
				{/if}
			</div>

			<!-- Requests Today -->
			<div class="flex items-center justify-between text-xs">
				<span class="flex items-center gap-1.5 text-muted-foreground">
					<Activity class="size-3" />
					Messages today
				</span>
				<span class="font-medium">{formatNumber(usage.messages_this_month)}</span>
			</div>

			<!-- Days Until Reset -->
			<div class="flex items-center justify-between text-xs">
				<span class="flex items-center gap-1.5 text-muted-foreground">
					<Calendar class="size-3" />
					Resets in
				</span>
				<span class="font-medium">{daysUntilReset} days</span>
			</div>
		</div>

	<!-- Full View -->
	{:else}
		<Card.Root>
			<Card.Header class="pb-3">
				<Card.Title class="flex items-center gap-2 text-base">
					<Zap class="size-4" />
					Usage & Quota
				</Card.Title>
				<Card.Description>
					Your current usage and limits
				</Card.Description>
			</Card.Header>
			<Card.Content class="space-y-4">
				<!-- Token Usage with Progress -->
				<div class="space-y-2">
					<div class="flex items-center justify-between">
						<span class="text-sm font-medium">Token Usage</span>
						{#if usage.quota}
							<span class="text-sm text-muted-foreground">
								{quotaPercentage.toFixed(1)}%
							</span>
						{/if}
					</div>

					{#if usage.quota}
						<div class="relative h-2 w-full overflow-hidden rounded-full bg-muted">
							<div
								class="h-full transition-all duration-500 {progressColor}"
								style="width: {Math.min(quotaPercentage, 100)}%"
							></div>
						</div>
						<div class="flex items-center justify-between text-xs text-muted-foreground">
							<span>{formatNumber(usage.quota.tokens_used)} used</span>
							<span>{formatNumber(usage.quota.tokens_limit)} limit</span>
						</div>
					{:else}
						<div class="text-2xl font-bold">{formatNumber(usage.tokens_this_month)}</div>
						<p class="text-xs text-muted-foreground">tokens this month</p>
					{/if}
				</div>

				<!-- Stats Grid -->
				<div class="grid grid-cols-2 gap-4 pt-2 border-t">
					<div>
						<div class="flex items-center gap-1.5 text-xs text-muted-foreground">
							<Activity class="size-3" />
							Messages This Month
						</div>
						<div class="text-lg font-semibold">{formatNumber(usage.messages_this_month)}</div>
					</div>
					<div>
						<div class="flex items-center gap-1.5 text-xs text-muted-foreground">
							<Calendar class="size-3" />
							Resets In
						</div>
						<div class="text-lg font-semibold">{daysUntilReset} days</div>
					</div>
				</div>
			</Card.Content>
		</Card.Root>
	{/if}

	<!-- Alert Notifications -->
	{#if showAlerts && !compact}
		{#if isWarning && !isCritical && !isBlocked}
			<Alert.Root class="mt-4 border-yellow-500/50 bg-yellow-500/10">
				<AlertTriangle class="size-4 text-yellow-500" />
				<Alert.Title class="text-yellow-700 dark:text-yellow-400">Usage Warning</Alert.Title>
				<Alert.Description class="text-yellow-600 dark:text-yellow-300">
					You've used {quotaPercentage.toFixed(0)}% of your monthly quota.
					Consider upgrading your plan to avoid interruptions.
				</Alert.Description>
				<div class="mt-3">
					<Button variant="outline" size="sm" onclick={() => goto('/billing')}>
						View Plans
					</Button>
				</div>
			</Alert.Root>
		{/if}

		{#if isCritical && !isBlocked}
			<Alert.Root variant="destructive" class="mt-4">
				<XCircle class="size-4" />
				<Alert.Title>Critical Usage</Alert.Title>
				<Alert.Description>
					You've used {quotaPercentage.toFixed(0)}% of your monthly quota!
					You will be blocked from making new requests once you reach 100%.
				</Alert.Description>
				<div class="mt-3">
					<Button variant="destructive" size="sm" onclick={() => goto('/billing')}>
						<ArrowUpCircle class="mr-1.5 size-4" />
						Upgrade Now
					</Button>
				</div>
			</Alert.Root>
		{/if}
	{/if}

	<!-- Blocked Modal -->
	<Dialog.Root bind:open={blockedModalOpen}>
		<Dialog.Content class="sm:max-w-md">
			<Dialog.Header>
				<Dialog.Title class="flex items-center gap-2 text-destructive">
					<XCircle class="size-5" />
					Quota Exceeded
				</Dialog.Title>
				<Dialog.Description>
					You've reached your monthly usage limit.
				</Dialog.Description>
			</Dialog.Header>

			<div class="space-y-4 py-4">
				<div class="rounded-lg bg-destructive/10 p-4">
					<div class="flex items-center justify-between">
						<span class="text-sm font-medium">Tokens Used</span>
						<span class="text-sm text-destructive font-semibold">
							{usage.quota ? formatNumber(usage.quota.tokens_used) : 0}
						</span>
					</div>
					<div class="mt-2">
						<Progress value={100} max={100} class="h-2" />
					</div>
					<div class="mt-1 flex items-center justify-between text-xs text-muted-foreground">
						<span>Limit: {usage.quota ? formatNumber(usage.quota.tokens_limit) : 0}</span>
						<span>Resets in {daysUntilReset} days</span>
					</div>
				</div>

				<p class="text-sm text-muted-foreground">
					To continue using the service, you can:
				</p>
				<ul class="list-disc list-inside text-sm text-muted-foreground space-y-1">
					<li>Upgrade to a higher plan for more tokens</li>
					<li>Wait {daysUntilReset} days for your quota to reset</li>
				</ul>
			</div>

			<Dialog.Footer class="flex-col gap-2 sm:flex-row">
				<Button variant="outline" onclick={() => blockedModalOpen = false} class="w-full sm:w-auto">
					Maybe Later
				</Button>
				<Button onclick={handleUpgrade} class="w-full sm:w-auto">
					<ArrowUpCircle class="mr-1.5 size-4" />
					Upgrade Plan
				</Button>
			</Dialog.Footer>
		</Dialog.Content>
	</Dialog.Root>
{/if}
