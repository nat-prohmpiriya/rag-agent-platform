<script lang="ts">
	import { onMount } from 'svelte';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import { Badge } from '$lib/components/ui/badge';
	import { Input } from '$lib/components/ui/input';
	import * as Select from '$lib/components/ui/select';
	import * as Table from '$lib/components/ui/table';
	import {
		Search,
		RefreshCw,
		ChevronLeft,
		ChevronRight,
		Filter,
		FileText,
		User,
		CreditCard,
		Settings,
		Shield,
		X
	} from 'lucide-svelte';
	import {
		getAuditLogs,
		getAuditActionTypes,
		getAuditTargetTypes,
		getAuditAdmins,
		type AuditLog,
		type AuditActionType,
		type AuditLogAdmin,
		type AuditLogFilters
	} from '$lib/api/admin';

	// State
	let logs = $state<AuditLog[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	// Pagination
	let currentPage = $state(1);
	let perPage = $state(20);
	let totalPages = $state(0);
	let totalItems = $state(0);

	// Filters
	let actionTypes = $state<AuditActionType[]>([]);
	let targetTypes = $state<string[]>([]);
	let admins = $state<AuditLogAdmin[]>([]);

	let selectedAction = $state<string | undefined>(undefined);
	let selectedAdmin = $state<string | undefined>(undefined);
	let selectedTargetType = $state<string | undefined>(undefined);
	let searchQuery = $state('');
	let showFilters = $state(false);

	// Selected log for detail view
	let selectedLog = $state<AuditLog | null>(null);

	onMount(async () => {
		await Promise.all([loadLogs(), loadFilterOptions()]);
	});

	async function loadLogs() {
		try {
			loading = true;
			error = null;

			const filters: AuditLogFilters = {};
			if (selectedAction) filters.action = selectedAction;
			if (selectedAdmin) filters.admin_id = selectedAdmin;
			if (selectedTargetType) filters.target_type = selectedTargetType;
			if (searchQuery) filters.search = searchQuery;

			const response = await getAuditLogs(currentPage, perPage, filters);
			logs = response.items;
			totalPages = response.pages;
			totalItems = response.total;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load audit logs';
		} finally {
			loading = false;
		}
	}

	async function loadFilterOptions() {
		try {
			const [actions, targets, adminList] = await Promise.all([
				getAuditActionTypes(),
				getAuditTargetTypes(),
				getAuditAdmins()
			]);
			actionTypes = actions;
			targetTypes = targets;
			admins = adminList;
		} catch (e) {
			console.error('Failed to load filter options:', e);
		}
	}

	function handleSearch() {
		currentPage = 1;
		loadLogs();
	}

	function clearFilters() {
		selectedAction = undefined;
		selectedAdmin = undefined;
		selectedTargetType = undefined;
		searchQuery = '';
		currentPage = 1;
		loadLogs();
	}

	function goToPage(page: number) {
		if (page >= 1 && page <= totalPages) {
			currentPage = page;
			loadLogs();
		}
	}

	function formatDate(dateString: string): string {
		const date = new Date(dateString);
		return date.toLocaleString();
	}

	function getActionBadgeVariant(
		action: string
	): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (action.includes('delete') || action.includes('ban')) return 'destructive';
		if (action.includes('create')) return 'default';
		if (action.includes('update') || action.includes('upgrade')) return 'secondary';
		return 'outline';
	}

	function getTargetIcon(targetType: string | null) {
		switch (targetType) {
			case 'user':
				return User;
			case 'plan':
				return CreditCard;
			case 'subscription':
				return FileText;
			case 'settings':
				return Settings;
			default:
				return Shield;
		}
	}

	function formatActionLabel(action: string): string {
		return action.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase());
	}
</script>

<svelte:head>
	<title>Audit Logs | Admin</title>
</svelte:head>

<div class="flex-1 space-y-6 p-6">
	<!-- Header -->
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-2xl font-bold">Audit Logs</h1>
			<p class="text-muted-foreground">Track admin actions and system changes</p>
		</div>
		<div class="flex items-center gap-2">
			<Button variant="outline" size="sm" onclick={() => (showFilters = !showFilters)}>
				<Filter class="mr-2 h-4 w-4" />
				Filters
			</Button>
			<Button variant="outline" onclick={loadLogs} disabled={loading}>
				<RefreshCw class="mr-2 h-4 w-4 {loading ? 'animate-spin' : ''}" />
				Refresh
			</Button>
		</div>
	</div>

	<!-- Filters Panel -->
	{#if showFilters}
		<Card.Root>
			<Card.Content class="pt-6">
				<div class="grid gap-4 md:grid-cols-4">
					<!-- Search -->
					<div class="space-y-2">
						<label class="text-sm font-medium">Search</label>
						<div class="relative">
							<Search class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
							<Input
								type="text"
								placeholder="Search in description..."
								class="pl-9"
								bind:value={searchQuery}
								onkeydown={(e) => e.key === 'Enter' && handleSearch()}
							/>
						</div>
					</div>

					<!-- Action Filter -->
					<div class="space-y-2">
						<label class="text-sm font-medium">Action</label>
						<Select.Root
							type="single"
							value={selectedAction}
							onValueChange={(v) => {
								selectedAction = v || undefined;
								handleSearch();
							}}
						>
							<Select.Trigger class="w-full">
								{selectedAction ? formatActionLabel(selectedAction) : 'All actions'}
							</Select.Trigger>
							<Select.Content>
								<Select.Item value="">All actions</Select.Item>
								{#each actionTypes as action}
									<Select.Item value={action.value}>{action.label}</Select.Item>
								{/each}
							</Select.Content>
						</Select.Root>
					</div>

					<!-- Admin Filter -->
					<div class="space-y-2">
						<label class="text-sm font-medium">Admin</label>
						<Select.Root
							type="single"
							value={selectedAdmin}
							onValueChange={(v) => {
								selectedAdmin = v || undefined;
								handleSearch();
							}}
						>
							<Select.Trigger class="w-full">
								{selectedAdmin ? admins.find((a) => a.id === selectedAdmin)?.email : 'All admins'}
							</Select.Trigger>
							<Select.Content>
								<Select.Item value="">All admins</Select.Item>
								{#each admins as admin}
									<Select.Item value={admin.id}>{admin.email}</Select.Item>
								{/each}
							</Select.Content>
						</Select.Root>
					</div>

					<!-- Target Type Filter -->
					<div class="space-y-2">
						<label class="text-sm font-medium">Target Type</label>
						<Select.Root
							type="single"
							value={selectedTargetType}
							onValueChange={(v) => {
								selectedTargetType = v || undefined;
								handleSearch();
							}}
						>
							<Select.Trigger class="w-full">
								{selectedTargetType || 'All types'}
							</Select.Trigger>
							<Select.Content>
								<Select.Item value="">All types</Select.Item>
								{#each targetTypes as type}
									<Select.Item value={type}>{type}</Select.Item>
								{/each}
							</Select.Content>
						</Select.Root>
					</div>
				</div>

				{#if selectedAction || selectedAdmin || selectedTargetType || searchQuery}
					<div class="mt-4 flex items-center gap-2">
						<span class="text-sm text-muted-foreground">Active filters:</span>
						{#if searchQuery}
							<Badge variant="secondary" class="gap-1">
								Search: {searchQuery}
								<button onclick={() => { searchQuery = ''; handleSearch(); }}>
									<X class="h-3 w-3" />
								</button>
							</Badge>
						{/if}
						{#if selectedAction}
							<Badge variant="secondary" class="gap-1">
								{formatActionLabel(selectedAction)}
								<button onclick={() => { selectedAction = undefined; handleSearch(); }}>
									<X class="h-3 w-3" />
								</button>
							</Badge>
						{/if}
						{#if selectedAdmin}
							<Badge variant="secondary" class="gap-1">
								{admins.find((a) => a.id === selectedAdmin)?.email}
								<button onclick={() => { selectedAdmin = undefined; handleSearch(); }}>
									<X class="h-3 w-3" />
								</button>
							</Badge>
						{/if}
						{#if selectedTargetType}
							<Badge variant="secondary" class="gap-1">
								{selectedTargetType}
								<button onclick={() => { selectedTargetType = undefined; handleSearch(); }}>
									<X class="h-3 w-3" />
								</button>
							</Badge>
						{/if}
						<Button variant="ghost" size="sm" onclick={clearFilters}>
							Clear all
						</Button>
					</div>
				{/if}
			</Card.Content>
		</Card.Root>
	{/if}

	<!-- Stats Cards -->
	<div class="grid gap-4 md:grid-cols-4">
		<Card.Root>
			<Card.Content class="pt-6">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm text-muted-foreground">Total Logs</p>
						<p class="text-2xl font-bold">{totalItems}</p>
					</div>
					<FileText class="h-8 w-8 text-muted-foreground" />
				</div>
			</Card.Content>
		</Card.Root>

		<Card.Root>
			<Card.Content class="pt-6">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm text-muted-foreground">Action Types</p>
						<p class="text-2xl font-bold">{actionTypes.length}</p>
					</div>
					<Shield class="h-8 w-8 text-muted-foreground" />
				</div>
			</Card.Content>
		</Card.Root>

		<Card.Root>
			<Card.Content class="pt-6">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm text-muted-foreground">Active Admins</p>
						<p class="text-2xl font-bold">{admins.length}</p>
					</div>
					<User class="h-8 w-8 text-muted-foreground" />
				</div>
			</Card.Content>
		</Card.Root>

		<Card.Root>
			<Card.Content class="pt-6">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm text-muted-foreground">Current Page</p>
						<p class="text-2xl font-bold">{currentPage} / {totalPages || 1}</p>
					</div>
					<FileText class="h-8 w-8 text-muted-foreground" />
				</div>
			</Card.Content>
		</Card.Root>
	</div>

	<!-- Logs Table -->
	<Card.Root>
		<Card.Content class="p-0">
			{#if loading && logs.length === 0}
				<div class="flex items-center justify-center py-12">
					<div class="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent">
					</div>
				</div>
			{:else if error}
				<div class="p-6 text-center">
					<p class="text-destructive">{error}</p>
					<Button onclick={loadLogs} class="mt-4">Retry</Button>
				</div>
			{:else if logs.length === 0}
				<div class="p-12 text-center">
					<FileText class="mx-auto h-12 w-12 text-muted-foreground" />
					<h3 class="mt-4 text-lg font-medium">No audit logs found</h3>
					<p class="text-muted-foreground">
						{#if selectedAction || selectedAdmin || selectedTargetType || searchQuery}
							Try adjusting your filters
						{:else}
							Audit logs will appear here when admin actions are performed
						{/if}
					</p>
				</div>
			{:else}
				<Table.Root>
					<Table.Header>
						<Table.Row>
							<Table.Head class="w-[180px]">Timestamp</Table.Head>
							<Table.Head>Admin</Table.Head>
							<Table.Head>Action</Table.Head>
							<Table.Head>Target</Table.Head>
							<Table.Head class="max-w-[300px]">Description</Table.Head>
							<Table.Head>IP Address</Table.Head>
						</Table.Row>
					</Table.Header>
					<Table.Body>
						{#each logs as log}
							<Table.Row
								class="cursor-pointer hover:bg-muted/50"
								onclick={() => (selectedLog = selectedLog?.id === log.id ? null : log)}
							>
								<Table.Cell class="font-mono text-sm">
									{formatDate(log.created_at)}
								</Table.Cell>
								<Table.Cell>
									{#if log.admin}
										<div class="flex items-center gap-2">
											<div class="flex h-6 w-6 items-center justify-center rounded-full bg-primary/10">
												<User class="h-3 w-3" />
											</div>
											<span class="text-sm">{log.admin.email}</span>
										</div>
									{:else}
										<span class="text-muted-foreground">System</span>
									{/if}
								</Table.Cell>
								<Table.Cell>
									<Badge variant={getActionBadgeVariant(log.action)}>
										{formatActionLabel(log.action)}
									</Badge>
								</Table.Cell>
								<Table.Cell>
									{#if log.target_type}
										{@const TargetIcon = getTargetIcon(log.target_type)}
										<div class="flex items-center gap-2">
											<TargetIcon class="h-4 w-4 text-muted-foreground" />
											<span class="text-sm capitalize">{log.target_type}</span>
										</div>
									{:else}
										<span class="text-muted-foreground">-</span>
									{/if}
								</Table.Cell>
								<Table.Cell class="max-w-[300px] truncate">
									{log.description}
								</Table.Cell>
								<Table.Cell class="font-mono text-sm">
									{log.ip_address || '-'}
								</Table.Cell>
							</Table.Row>

							<!-- Expandable Details Row -->
							{#if selectedLog?.id === log.id}
								<Table.Row>
									<Table.Cell colspan={6} class="bg-muted/30 p-4">
										<div class="space-y-4">
											<div class="grid gap-4 md:grid-cols-2">
												<div>
													<h4 class="mb-2 text-sm font-medium">Log Details</h4>
													<dl class="space-y-1 text-sm">
														<div class="flex">
															<dt class="w-24 text-muted-foreground">Log ID:</dt>
															<dd class="font-mono">{log.id}</dd>
														</div>
														{#if log.target_id}
															<div class="flex">
																<dt class="w-24 text-muted-foreground">Target ID:</dt>
																<dd class="font-mono">{log.target_id}</dd>
															</div>
														{/if}
														{#if log.user_agent}
															<div class="flex">
																<dt class="w-24 text-muted-foreground">User Agent:</dt>
																<dd class="max-w-md truncate" title={log.user_agent}>
																	{log.user_agent}
																</dd>
															</div>
														{/if}
													</dl>
												</div>
												{#if log.details}
													<div>
														<h4 class="mb-2 text-sm font-medium">Additional Details</h4>
														<pre class="max-h-40 overflow-auto rounded bg-muted p-2 text-xs">{JSON.stringify(log.details, null, 2)}</pre>
													</div>
												{/if}
											</div>
										</div>
									</Table.Cell>
								</Table.Row>
							{/if}
						{/each}
					</Table.Body>
				</Table.Root>

				<!-- Pagination -->
				{#if totalPages > 1}
					<div class="flex items-center justify-between border-t px-4 py-3">
						<div class="text-sm text-muted-foreground">
							Showing {(currentPage - 1) * perPage + 1} to {Math.min(currentPage * perPage, totalItems)} of {totalItems} logs
						</div>
						<div class="flex items-center gap-2">
							<Button
								variant="outline"
								size="sm"
								onclick={() => goToPage(currentPage - 1)}
								disabled={currentPage <= 1}
							>
								<ChevronLeft class="h-4 w-4" />
								Previous
							</Button>
							<div class="flex items-center gap-1">
								{#each Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
									const startPage = Math.max(1, currentPage - 2);
									return startPage + i;
								}).filter((p) => p <= totalPages) as page}
									<Button
										variant={page === currentPage ? 'default' : 'outline'}
										size="sm"
										onclick={() => goToPage(page)}
									>
										{page}
									</Button>
								{/each}
							</div>
							<Button
								variant="outline"
								size="sm"
								onclick={() => goToPage(currentPage + 1)}
								disabled={currentPage >= totalPages}
							>
								Next
								<ChevronRight class="h-4 w-4" />
							</Button>
						</div>
					</div>
				{/if}
			{/if}
		</Card.Content>
	</Card.Root>
</div>
