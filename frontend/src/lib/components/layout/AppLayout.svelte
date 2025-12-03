<script lang="ts">
	import type { Snippet } from 'svelte';
	import { onMount } from 'svelte';
	import { Button } from '$lib/components/ui/button';
	import * as Sheet from '$lib/components/ui/sheet';
	import * as Tooltip from '$lib/components/ui/tooltip';
	import Sidebar from './Sidebar.svelte';
	import { Menu } from 'lucide-svelte';
	import { sidebar } from '$lib/stores';
	import type { Project } from '$lib/api';

	let { children, user, currentProject, currentProjectId, projects, loading, onLogout, onProjectSelect, onNewProject }: {
		children?: Snippet;
		user?: { name: string; email: string; avatar?: string } | null;
		currentProject?: { id: string; name: string } | null;
		currentProjectId?: string | null;
		projects?: Project[];
		loading?: boolean;
		onLogout?: () => void;
		onProjectSelect?: (projectId: string | null) => void;
		onNewProject?: () => void;
	} = $props();

	let sidebarOpen = $state(false);

	onMount(() => {
		sidebar.initialize();
	});

	function handleToggle() {
		sidebar.toggle();
	}
</script>

<Tooltip.Provider>
	<div class="flex min-h-screen bg-background">
		<!-- Mobile sidebar trigger (floating button) -->
		<div class="fixed top-4 left-4 z-50 md:hidden">
			<Sheet.Root bind:open={sidebarOpen}>
				<Sheet.Trigger>
					{#snippet child({ props })}
						<button
							{...props}
							class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-background border shadow-sm hover:bg-accent hover:text-accent-foreground h-10 w-10"
						>
							<Menu class="h-5 w-5" />
							<span class="sr-only">Toggle sidebar</span>
						</button>
					{/snippet}
				</Sheet.Trigger>
				<Sheet.Content side="left" class="w-64 p-0">
					<Sidebar
						{currentProject}
						{currentProjectId}
						{projects}
						{loading}
						{onProjectSelect}
						{onNewProject}
						{user}
						{onLogout}
					/>
				</Sheet.Content>
			</Sheet.Root>
		</div>

		<!-- Desktop sidebar -->
		<div class="hidden md:block">
			<div class="sticky top-0 h-screen">
				<Sidebar
					{currentProject}
					{currentProjectId}
					{projects}
					{loading}
					{onProjectSelect}
					{onNewProject}
					{user}
					{onLogout}
					collapsed={sidebar.collapsed}
					onToggle={handleToggle}
				/>
			</div>
		</div>

		<!-- Main content -->
		<main class="flex-1 min-w-0">
			{#if children}
				{@render children()}
			{/if}
		</main>
	</div>
</Tooltip.Provider>
