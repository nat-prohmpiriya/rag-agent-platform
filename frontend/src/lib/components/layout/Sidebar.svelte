<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { Button } from '$lib/components/ui/button';
	import { ScrollArea } from '$lib/components/ui/scroll-area';
	import { Separator } from '$lib/components/ui/separator';
	import * as Tooltip from '$lib/components/ui/tooltip';
	import { MessageSquare, FileText, Users, Database, Sliders, Settings, ChevronLeft, ChevronRight, FolderOpen, Plus, ExternalLink } from 'lucide-svelte';
	import ProjectList from '$lib/components/projects/ProjectList.svelte';
	import type { Project } from '$lib/api';

	let {
		currentProject,
		projects = [],
		currentProjectId = null,
		loading = false,
		onProjectSelect,
		onNewProject,
		collapsed = false,
		onToggle
	} = $props<{
		currentProject?: { id: string; name: string } | null;
		projects?: Project[];
		currentProjectId?: string | null;
		loading?: boolean;
		onProjectSelect?: (projectId: string | null) => void;
		onNewProject?: () => void;
		collapsed?: boolean;
		onToggle?: () => void;
	}>();

	interface NavItem {
		label: string;
		href: string;
		icon: typeof MessageSquare;
	}

	const navItems: NavItem[] = [
		{ label: 'Chat', href: '/chat', icon: MessageSquare },
		{ label: 'Documents', href: '/documents', icon: FileText },
		{ label: 'Agents', href: '/agents', icon: Users },
		{ label: 'SQL Query', href: '/sql', icon: Database },
		{ label: 'Fine-tuning', href: '/finetune', icon: Sliders },
		{ label: 'Settings', href: '/settings', icon: Settings }
	];

	function isActive(href: string): boolean {
		return $page.url.pathname.startsWith(href);
	}

	function handleProjectSelect(id: string | null) {
		onProjectSelect?.(id);
	}

	function handleViewProject() {
		if (currentProjectId) {
			goto(`/projects/${currentProjectId}`);
		}
	}
</script>

<aside class="flex h-full flex-col border-r bg-background transition-all duration-300 {collapsed ? 'w-16' : 'w-64'}">
	<!-- Project selector -->
	{#if !collapsed}
		<div class="p-4">
			<ProjectList
				{projects}
				{currentProjectId}
				{loading}
				onSelect={handleProjectSelect}
				onCreate={onNewProject ?? (() => {})}
			/>
			<!-- View project details link -->
			{#if currentProjectId}
				<Button
					variant="ghost"
					size="sm"
					class="mt-2 w-full justify-start text-xs text-muted-foreground"
					onclick={handleViewProject}
				>
					<ExternalLink class="mr-2 h-3 w-3" />
					View Project Details
				</Button>
			{/if}
		</div>
		<Separator />
	{:else}
		<div class="flex justify-center p-4">
			<Tooltip.Root>
				<Tooltip.Trigger>
					{#snippet child({ props })}
						<Button {...props} variant="ghost" size="icon" onclick={onNewProject}>
							<FolderOpen class="h-5 w-5" />
						</Button>
					{/snippet}
				</Tooltip.Trigger>
				<Tooltip.Portal>
					<Tooltip.Content side="right">
						{currentProject?.name || 'Select project'}
					</Tooltip.Content>
				</Tooltip.Portal>
			</Tooltip.Root>
		</div>
		<Separator />
	{/if}

	<!-- Navigation -->
	<ScrollArea class="flex-1 px-2 py-4">
		<nav class="flex flex-col gap-1">
			{#each navItems as item}
				{@const Icon = item.icon}
				{#if collapsed}
					<Tooltip.Root>
						<Tooltip.Trigger>
							{#snippet child({ props })}
								<a
									{...props}
									href={item.href}
									class="flex items-center justify-center rounded-lg p-2 text-sm transition-colors hover:bg-accent hover:text-accent-foreground {isActive(item.href) ? 'bg-accent text-accent-foreground' : ''}"
								>
									<Icon class="h-5 w-5" />
								</a>
							{/snippet}
						</Tooltip.Trigger>
						<Tooltip.Portal>
							<Tooltip.Content side="right">
								{item.label}
							</Tooltip.Content>
						</Tooltip.Portal>
					</Tooltip.Root>
				{:else}
					<a
						href={item.href}
						class="flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors hover:bg-accent hover:text-accent-foreground {isActive(item.href) ? 'bg-accent text-accent-foreground' : ''}"
					>
						<Icon class="h-4 w-4" />
						{item.label}
					</a>
				{/if}
			{/each}
		</nav>
	</ScrollArea>

	<!-- Toggle button & Footer -->
	<div class="border-t p-2">
		{#if collapsed}
			<Tooltip.Root>
				<Tooltip.Trigger>
					{#snippet child({ props })}
						<Button {...props} variant="ghost" size="icon" class="w-full" onclick={onToggle}>
							<ChevronRight class="h-4 w-4" />
						</Button>
					{/snippet}
				</Tooltip.Trigger>
				<Tooltip.Portal>
					<Tooltip.Content side="right">
						Expand sidebar
					</Tooltip.Content>
				</Tooltip.Portal>
			</Tooltip.Root>
		{:else}
			<Button variant="ghost" class="w-full justify-start" onclick={onToggle}>
				<ChevronLeft class="mr-2 h-4 w-4" />
				Collapse
			</Button>
			<p class="mt-2 text-center text-xs text-muted-foreground">RAG Agent v1.0</p>
		{/if}
	</div>
</aside>
