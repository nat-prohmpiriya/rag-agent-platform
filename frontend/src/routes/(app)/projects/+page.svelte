<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { Folder, Plus, Search, Trash2, FileText, MessageSquare } from 'lucide-svelte';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Badge } from '$lib/components/ui/badge';
	import { projectsApi, type ProjectDetail, type ProjectCreate, type ProjectUpdate } from '$lib/api';
	import ProjectDialog from '$lib/components/projects/ProjectDialog.svelte';

	let projects = $state<ProjectDetail[]>([]);
	let loading = $state(true);
	let searchQuery = $state('');
	let showCreateDialog = $state(false);

	let filteredProjects = $derived(
		searchQuery
			? projects.filter(
					(p) =>
						p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
						(p.description?.toLowerCase().includes(searchQuery.toLowerCase()) ?? false)
				)
			: projects
	);

	onMount(async () => {
		await loadProjects();
	});

	async function loadProjects() {
		try {
			const response = await projectsApi.list(1, 100);
			// Get detail for each project to get counts
			const projectDetails = await Promise.all(
				response.items.map((p) => projectsApi.get(p.id))
			);
			projects = projectDetails;
		} catch (e) {
			console.error('Failed to load projects:', e);
		} finally {
			loading = false;
		}
	}

	async function handleCreate(data: ProjectCreate | ProjectUpdate) {
		try {
			const newProject = await projectsApi.create(data as ProjectCreate);
			// Get project detail with counts
			const projectDetail = await projectsApi.get(newProject.id);
			projects = [projectDetail, ...projects];
			showCreateDialog = false;
		} catch (e) {
			console.error('Failed to create project:', e);
		}
	}

	async function handleDelete(id: string, event: MouseEvent) {
		event.stopPropagation();
		try {
			await projectsApi.delete(id);
			projects = projects.filter((p) => p.id !== id);
		} catch (e) {
			console.error('Failed to delete project:', e);
		}
	}

	function handleClick(id: string) {
		goto(`/projects/${id}`);
	}

	function formatDate(dateString: string): string {
		const date = new Date(dateString);
		const now = new Date();
		const diff = now.getTime() - date.getTime();
		const days = Math.floor(diff / (1000 * 60 * 60 * 24));

		if (days === 0) return 'Today';
		if (days === 1) return 'Yesterday';
		if (days < 7) return `${days} days ago`;
		return date.toLocaleDateString();
	}
</script>

<svelte:head>
	<title>Projects | RAG Agent</title>
</svelte:head>

<div class="flex h-full flex-col">
	<!-- Header -->
	<div class="border-b bg-background p-4">
		<div class="flex items-center justify-between">
			<div class="flex items-center gap-2">
				<Folder class="size-5" />
				<h1 class="text-lg font-semibold">Projects</h1>
				{#if projects.length > 0}
					<span class="text-sm text-muted-foreground">({projects.length})</span>
				{/if}
			</div>

			<Button size="sm" onclick={() => (showCreateDialog = true)}>
				<Plus class="mr-2 size-4" />
				New Project
			</Button>
		</div>

		<!-- Search -->
		<div class="mt-4 relative">
			<Search class="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
			<Input
				type="search"
				placeholder="Search projects..."
				class="pl-9"
				bind:value={searchQuery}
			/>
		</div>
	</div>

	<!-- Content -->
	<div class="flex-1 overflow-auto p-4">
		<div class="mx-auto max-w-3xl space-y-2">
			{#if loading}
				<div class="flex items-center justify-center py-12">
					<div
						class="size-8 animate-spin rounded-full border-4 border-muted border-t-primary"
					></div>
				</div>
			{:else if filteredProjects.length === 0}
				<div class="rounded-lg border border-dashed flex flex-col items-center p-12">
					<Folder class="size-12 text-muted-foreground/50" />
					<h3 class="mt-4 text-lg font-medium">No projects</h3>
					<p class="mt-1 text-sm text-muted-foreground">
						{#if searchQuery}
							No projects matching "{searchQuery}". Try a different search.
						{:else}
							Create your first project to organize documents and conversations.
						{/if}
					</p>
					<Button class="mt-4" onclick={() => (showCreateDialog = true)}>
						<Plus class="mr-2 size-4" />
						Create Project
					</Button>
				</div>
			{:else}
				{#each filteredProjects as project (project.id)}
					<button
						class="w-full flex items-center justify-between rounded-lg border p-4 text-left hover:bg-accent transition-colors group"
						onclick={() => handleClick(project.id)}
					>
						<div class="flex-1 min-w-0">
							<div class="flex items-center gap-2">
								<h3 class="font-medium truncate">{project.name}</h3>
							</div>
							{#if project.description}
								<p class="text-sm text-muted-foreground truncate mt-1">
									{project.description}
								</p>
							{/if}
							<div class="flex items-center gap-3 mt-2">
								<Badge variant="secondary" class="gap-1 text-xs">
									<FileText class="size-3" />
									{project.document_count}
								</Badge>
								<Badge variant="secondary" class="gap-1 text-xs">
									<MessageSquare class="size-3" />
									{project.conversation_count}
								</Badge>
								<span class="text-xs text-muted-foreground">
									{formatDate(project.updated_at)}
								</span>
							</div>
						</div>
						<Button
							variant="ghost"
							size="icon"
							class="opacity-0 group-hover:opacity-100 transition-opacity"
							onclick={(e) => handleDelete(project.id, e)}
						>
							<Trash2 class="size-4 text-destructive" />
						</Button>
					</button>
				{/each}
			{/if}
		</div>
	</div>
</div>

<!-- Create Project Dialog -->
<ProjectDialog bind:open={showCreateDialog} project={null} onSave={handleCreate} />
