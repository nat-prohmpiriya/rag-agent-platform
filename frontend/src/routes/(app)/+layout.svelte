<script lang="ts">
	import type { Snippet } from 'svelte';
	import { goto } from '$app/navigation';
	import { auth } from '$lib/stores';
	import { getUserDisplayName } from '$lib/types';
	import AppLayout from '$lib/components/layout/AppLayout.svelte';

	let { children }: { children: Snippet } = $props();

	// Auth guard - redirect to login if not authenticated
	$effect(() => {
		if (!auth.isLoading && !auth.isAuthenticated) {
			goto('/login');
		}
	});

	function handleLogout() {
		auth.logout();
		goto('/login');
	}
</script>

{#if auth.isLoading}
	<div class="min-h-screen flex items-center justify-center bg-background">
		<div class="flex flex-col items-center gap-4">
			<svg class="h-8 w-8 animate-spin text-primary" viewBox="0 0 24 24">
				<circle
					class="opacity-25"
					cx="12"
					cy="12"
					r="10"
					stroke="currentColor"
					stroke-width="4"
					fill="none"
				/>
				<path
					class="opacity-75"
					fill="currentColor"
					d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
				/>
			</svg>
			<p class="text-muted-foreground">Loading...</p>
		</div>
	</div>
{:else if auth.isAuthenticated}
	<AppLayout
		user={auth.user ? { name: getUserDisplayName(auth.user), email: auth.user.email } : null}
		onLogout={handleLogout}
	>
		{@render children()}
	</AppLayout>
{/if}
