<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import { Badge } from '$lib/components/ui/badge';
	import { Progress } from '$lib/components/ui/progress';
	import {
		Activity,
		Database,
		Server,
		Zap,
		RefreshCw,
		CircleCheck,
		TriangleAlert,
		CircleX,
		Info,
		Clock
	} from 'lucide-svelte';
	import { getSystemHealth, type SystemHealth, type ServiceStatus } from '$lib/api/admin';

	let health = $state<SystemHealth | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let lastUpdated = $state<Date | null>(null);
	let autoRefresh = $state(true);
	let refreshInterval: ReturnType<typeof setInterval> | null = null;

	onMount(async () => {
		await loadHealth();
		if (autoRefresh) {
			startAutoRefresh();
		}
	});

	onDestroy(() => {
		stopAutoRefresh();
	});

	async function loadHealth() {
		try {
			loading = true;
			error = null;
			health = await getSystemHealth();
			lastUpdated = new Date();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load system health';
		} finally {
			loading = false;
		}
	}

	function startAutoRefresh() {
		stopAutoRefresh();
		refreshInterval = setInterval(loadHealth, 30000); // Refresh every 30 seconds
	}

	function stopAutoRefresh() {
		if (refreshInterval) {
			clearInterval(refreshInterval);
			refreshInterval = null;
		}
	}

	function toggleAutoRefresh() {
		autoRefresh = !autoRefresh;
		if (autoRefresh) {
			startAutoRefresh();
		} else {
			stopAutoRefresh();
		}
	}

	function getStatusBadgeVariant(
		status: ServiceStatus
	): 'default' | 'secondary' | 'destructive' | 'outline' {
		switch (status) {
			case 'healthy':
				return 'default';
			case 'degraded':
				return 'secondary';
			case 'unhealthy':
				return 'destructive';
			default:
				return 'outline';
		}
	}

	function formatResponseTime(ms: number | null): string {
		if (ms === null) return '-';
		return `${ms.toFixed(0)}ms`;
	}

	function formatBytes(mb: number): string {
		if (mb >= 1024) {
			return `${(mb / 1024).toFixed(1)} GB`;
		}
		return `${mb.toFixed(1)} MB`;
	}

	function formatUptime(timestamp: string): string {
		const date = new Date(timestamp);
		return date.toLocaleString();
	}
</script>

<svelte:head>
	<title>System Monitoring | Admin</title>
</svelte:head>

<div class="flex-1 space-y-6 p-6">
	<!-- Header -->
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-2xl font-bold">System Monitoring</h1>
			<p class="text-muted-foreground">Health and performance monitoring</p>
		</div>
		<div class="flex items-center gap-4">
			{#if lastUpdated}
				<span class="flex items-center gap-1 text-sm text-muted-foreground">
					<Clock class="h-4 w-4" />
					Last updated: {lastUpdated.toLocaleTimeString()}
				</span>
			{/if}
			<Button variant={autoRefresh ? 'default' : 'outline'} size="sm" onclick={toggleAutoRefresh}>
				{autoRefresh ? 'Auto-refresh ON' : 'Auto-refresh OFF'}
			</Button>
			<Button variant="outline" onclick={loadHealth} disabled={loading}>
				<RefreshCw class="mr-2 h-4 w-4 {loading ? 'animate-spin' : ''}" />
				Refresh
			</Button>
		</div>
	</div>

	{#if loading && !health}
		<div class="flex items-center justify-center py-12">
			<div class="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent">
			</div>
		</div>
	{:else if error}
		<Card.Root class="border-destructive">
			<Card.Content class="pt-6">
				<p class="text-destructive">{error}</p>
				<Button onclick={loadHealth} class="mt-4">Retry</Button>
			</Card.Content>
		</Card.Root>
	{:else if health}
		<!-- Overall Status Banner -->
		<Card.Root
			class="border-2 {health.overall_status === 'healthy'
				? 'border-green-500 bg-green-50 dark:bg-green-950/20'
				: health.overall_status === 'degraded'
					? 'border-yellow-500 bg-yellow-50 dark:bg-yellow-950/20'
					: 'border-red-500 bg-red-50 dark:bg-red-950/20'}"
		>
			<Card.Content class="flex items-center justify-between py-4">
				<div class="flex items-center gap-3">
					{#if health.overall_status === 'healthy'}
						<CircleCheck class="h-8 w-8 text-green-600" />
					{:else if health.overall_status === 'degraded'}
						<TriangleAlert class="h-8 w-8 text-yellow-600" />
					{:else if health.overall_status === 'unhealthy'}
						<CircleX class="h-8 w-8 text-red-600" />
					{:else}
						<Info class="h-8 w-8 text-gray-600" />
					{/if}
					<div>
						<h2 class="text-lg font-semibold">
							System Status: <span class="capitalize">{health.overall_status}</span>
						</h2>
						<p class="text-sm text-muted-foreground">
							Last checked: {formatUptime(health.timestamp)}
						</p>
					</div>
				</div>
				<Badge variant={getStatusBadgeVariant(health.overall_status)} class="text-sm">
					{health.overall_status.toUpperCase()}
				</Badge>
			</Card.Content>
		</Card.Root>

		<!-- Service Cards -->
		<div class="grid gap-6 md:grid-cols-3">
			<!-- LiteLLM Proxy -->
			<Card.Root>
				<Card.Header class="flex flex-row items-center justify-between space-y-0 pb-2">
					<div class="flex items-center gap-2">
						<div class="rounded-lg bg-blue-100 p-2 dark:bg-blue-900">
							<Zap class="h-5 w-5 text-blue-600 dark:text-blue-400" />
						</div>
						<div>
							<Card.Title class="text-base">LiteLLM Proxy</Card.Title>
							<p class="text-xs text-muted-foreground">{health.litellm.url}</p>
						</div>
					</div>
					<Badge variant={getStatusBadgeVariant(health.litellm.status)}>
						{health.litellm.status}
					</Badge>
				</Card.Header>
				<Card.Content class="space-y-4">
					{#if health.litellm.error}
						<div class="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
							{health.litellm.error}
						</div>
					{:else}
						<div class="space-y-3">
							<div class="flex justify-between text-sm">
								<span class="text-muted-foreground">Response Time</span>
								<span class="font-medium">{formatResponseTime(health.litellm.response_time_ms)}</span
								>
							</div>
							<div class="flex justify-between text-sm">
								<span class="text-muted-foreground">Models Available</span>
								<span class="font-medium">{health.litellm.models_available}</span>
							</div>
						</div>
					{/if}
				</Card.Content>
			</Card.Root>

			<!-- PostgreSQL -->
			<Card.Root>
				<Card.Header class="flex flex-row items-center justify-between space-y-0 pb-2">
					<div class="flex items-center gap-2">
						<div class="rounded-lg bg-green-100 p-2 dark:bg-green-900">
							<Database class="h-5 w-5 text-green-600 dark:text-green-400" />
						</div>
						<div>
							<Card.Title class="text-base">PostgreSQL</Card.Title>
							<p class="text-xs text-muted-foreground">{health.postgresql.host}</p>
						</div>
					</div>
					<Badge variant={getStatusBadgeVariant(health.postgresql.status)}>
						{health.postgresql.status}
					</Badge>
				</Card.Header>
				<Card.Content class="space-y-4">
					{#if health.postgresql.error}
						<div class="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
							{health.postgresql.error}
						</div>
					{:else}
						<div class="space-y-3">
							<div class="flex justify-between text-sm">
								<span class="text-muted-foreground">Response Time</span>
								<span class="font-medium"
									>{formatResponseTime(health.postgresql.response_time_ms)}</span
								>
							</div>
							<div>
								<div class="mb-1 flex justify-between text-sm">
									<span class="text-muted-foreground">Connections</span>
									<span class="font-medium">
										{health.postgresql.active_connections} / {health.postgresql.max_connections}
									</span>
								</div>
								<Progress
									value={(health.postgresql.active_connections / health.postgresql.max_connections) *
										100}
									class="h-2"
								/>
							</div>
							<div class="flex justify-between text-sm">
								<span class="text-muted-foreground">Database Size</span>
								<span class="font-medium">{formatBytes(health.postgresql.database_size_mb)}</span>
							</div>
						</div>
					{/if}
				</Card.Content>
			</Card.Root>

			<!-- Redis -->
			<Card.Root>
				<Card.Header class="flex flex-row items-center justify-between space-y-0 pb-2">
					<div class="flex items-center gap-2">
						<div class="rounded-lg bg-red-100 p-2 dark:bg-red-900">
							<Server class="h-5 w-5 text-red-600 dark:text-red-400" />
						</div>
						<div>
							<Card.Title class="text-base">Redis</Card.Title>
							<p class="text-xs text-muted-foreground">
								{health.redis.host}:{health.redis.port}
							</p>
						</div>
					</div>
					<Badge variant={getStatusBadgeVariant(health.redis.status)}>
						{health.redis.status}
					</Badge>
				</Card.Header>
				<Card.Content class="space-y-4">
					{#if health.redis.error}
						<div class="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
							{health.redis.error}
						</div>
					{:else}
						<div class="space-y-3">
							<div class="flex justify-between text-sm">
								<span class="text-muted-foreground">Response Time</span>
								<span class="font-medium">{formatResponseTime(health.redis.response_time_ms)}</span>
							</div>
							<div>
								<div class="mb-1 flex justify-between text-sm">
									<span class="text-muted-foreground">Memory</span>
									<span class="font-medium">
										{formatBytes(health.redis.used_memory_mb)}
										{#if health.redis.max_memory_mb > 0}
											/ {formatBytes(health.redis.max_memory_mb)}
										{/if}
									</span>
								</div>
								{#if health.redis.max_memory_mb > 0}
									<Progress
										value={(health.redis.used_memory_mb / health.redis.max_memory_mb) * 100}
										class="h-2"
									/>
								{/if}
							</div>
							<div class="flex justify-between text-sm">
								<span class="text-muted-foreground">Connected Clients</span>
								<span class="font-medium">{health.redis.connected_clients}</span>
							</div>
							<div class="flex justify-between text-sm">
								<span class="text-muted-foreground">Hit Rate</span>
								<span class="font-medium">{health.redis.hit_rate.toFixed(1)}%</span>
							</div>
						</div>
					{/if}
				</Card.Content>
			</Card.Root>
		</div>

		<!-- Performance Metrics (placeholder for future) -->
		<Card.Root>
			<Card.Header>
				<Card.Title class="flex items-center gap-2">
					<Activity class="h-5 w-5" />
					Performance Metrics
				</Card.Title>
				<Card.Description>Real-time performance monitoring</Card.Description>
			</Card.Header>
			<Card.Content>
				<div class="grid gap-4 md:grid-cols-4">
					<div class="rounded-lg border p-4">
						<p class="text-sm text-muted-foreground">Requests/sec</p>
						<p class="text-2xl font-bold">-</p>
					</div>
					<div class="rounded-lg border p-4">
						<p class="text-sm text-muted-foreground">Avg Response Time</p>
						<p class="text-2xl font-bold">-</p>
					</div>
					<div class="rounded-lg border p-4">
						<p class="text-sm text-muted-foreground">Error Rate</p>
						<p class="text-2xl font-bold">-</p>
					</div>
					<div class="rounded-lg border p-4">
						<p class="text-sm text-muted-foreground">Active Users</p>
						<p class="text-2xl font-bold">-</p>
					</div>
				</div>
				<p class="mt-4 text-center text-sm text-muted-foreground">
					Performance metrics collection coming soon
				</p>
			</Card.Content>
		</Card.Root>
	{/if}
</div>
