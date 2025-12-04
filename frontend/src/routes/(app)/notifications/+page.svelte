<script lang="ts">
	import { onMount } from 'svelte';
	import { Bell, Check, Trash2, Loader2 } from 'lucide-svelte';
	import { Button } from '$lib/components/ui/button';
	import * as Select from '$lib/components/ui/select';
	import { notificationStore } from '$lib/stores';
	import { NotificationItem } from '$lib/components/notifications';

	type FilterType = 'all' | 'unread';

	let filter = $state<FilterType>('all');
	let markingAllRead = $state(false);

	// Derived state from store
	const notifications = $derived(notificationStore.notifications);
	const loading = $derived(notificationStore.loading);
	const hasUnread = $derived(notificationStore.hasUnread);
	const currentPage = $derived(notificationStore.currentPage);
	const totalPages = $derived(notificationStore.totalPages);
	const total = $derived(notificationStore.total);

	const filterOptions: { value: FilterType; label: string }[] = [
		{ value: 'all', label: 'All' },
		{ value: 'unread', label: 'Unread only' }
	];

	onMount(async () => {
		await loadNotifications();
	});

	async function loadNotifications() {
		await notificationStore.fetchNotifications({
			page: 1,
			per_page: 20,
			unread_only: filter === 'unread'
		});
	}

	async function handleFilterChange(value: string | undefined) {
		if (value) {
			filter = value as FilterType;
			await loadNotifications();
		}
	}

	async function handleMarkAsRead(id: string) {
		await notificationStore.markAsRead(id);
	}

	async function handleMarkAllAsRead() {
		markingAllRead = true;
		await notificationStore.markAllAsRead();
		markingAllRead = false;
	}

	async function handleDelete(id: string) {
		await notificationStore.deleteNotification(id);
	}

	async function handlePageChange(page: number) {
		await notificationStore.fetchNotifications({
			page,
			per_page: 20,
			unread_only: filter === 'unread'
		});
	}
</script>

<svelte:head>
	<title>Notifications | RAG Agent</title>
</svelte:head>

<div class="flex h-full flex-col">
	<!-- Content -->
	<div class="flex-1 overflow-auto p-8">
		<div class="mx-auto max-w-3xl">
			<!-- Header -->
			<div class="flex items-center justify-between mb-6">
				<div class="flex items-center gap-3">
					<Bell class="size-8 text-foreground" />
					<h1 class="text-3xl font-semibold text-foreground">Notifications</h1>
				</div>
				{#if hasUnread}
					<Button
						variant="outline"
						size="sm"
						onclick={handleMarkAllAsRead}
						disabled={markingAllRead}
					>
						{#if markingAllRead}
							<Loader2 class="size-4 animate-spin mr-2" />
						{:else}
							<Check class="size-4 mr-2" />
						{/if}
						Mark all as read
					</Button>
				{/if}
			</div>

			<!-- Filter -->
			<div class="flex items-center justify-between mb-4">
				<span class="text-sm text-muted-foreground">
					{total} notification{total !== 1 ? 's' : ''}
				</span>
				<div class="flex items-center gap-2 text-sm text-muted-foreground">
					<span>Filter by</span>
					<Select.Root type="single" onValueChange={handleFilterChange}>
						<Select.Trigger class="w-32 h-8">
							<span>{filterOptions.find((o) => o.value === filter)?.label || 'All'}</span>
						</Select.Trigger>
						<Select.Content align="end">
							{#each filterOptions as option}
								<Select.Item value={option.value}>{option.label}</Select.Item>
							{/each}
						</Select.Content>
					</Select.Root>
				</div>
			</div>

			<!-- Notification List -->
			<div class="bg-white rounded-lg border border-border overflow-hidden">
				{#if loading && notifications.length === 0}
					<div class="flex items-center justify-center py-12">
						<div
							class="size-8 animate-spin rounded-full border-4 border-muted border-t-primary"
						></div>
					</div>
				{:else if notifications.length === 0}
					<div class="flex flex-col items-center p-12 text-center">
						<Bell class="size-12 text-muted-foreground/50" />
						<h3 class="mt-4 text-lg font-medium">No notifications</h3>
						<p class="mt-1 text-sm text-muted-foreground">
							{#if filter === 'unread'}
								You're all caught up! No unread notifications.
							{:else}
								You don't have any notifications yet.
							{/if}
						</p>
					</div>
				{:else}
					<div class="divide-y">
						{#each notifications as notification (notification.id)}
							<div class="group relative">
								<NotificationItem
									{notification}
									onMarkAsRead={handleMarkAsRead}
									onDelete={handleDelete}
								/>
								<!-- Delete button overlay on hover -->
								<div class="absolute right-4 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
									<Button
										variant="ghost"
										size="icon"
										class="size-8 text-muted-foreground hover:text-destructive hover:bg-destructive/10"
										onclick={() => handleDelete(notification.id)}
									>
										<Trash2 class="size-4" />
									</Button>
								</div>
							</div>
						{/each}
					</div>

					<!-- Pagination -->
					{#if totalPages > 1}
						<div class="flex items-center justify-center gap-2 p-4 border-t">
							<Button
								variant="outline"
								size="sm"
								disabled={currentPage <= 1 || loading}
								onclick={() => handlePageChange(currentPage - 1)}
							>
								Previous
							</Button>
							<span class="text-sm text-muted-foreground">
								Page {currentPage} of {totalPages}
							</span>
							<Button
								variant="outline"
								size="sm"
								disabled={currentPage >= totalPages || loading}
								onclick={() => handlePageChange(currentPage + 1)}
							>
								Next
							</Button>
						</div>
					{/if}
				{/if}
			</div>
		</div>
	</div>
</div>
