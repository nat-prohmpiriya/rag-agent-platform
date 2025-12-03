<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import {
		FolderOpen,
		FileText,
		MessageSquare,
		ArrowLeft,
		Pencil,
		Trash2,
		Plus,
		X
	} from 'lucide-svelte';
	import { Button } from '$lib/components/ui/button';
	import { Badge } from '$lib/components/ui/badge';
	import * as Tabs from '$lib/components/ui/tabs';
	import { projectsApi, type ProjectDetail, type Document, type ProjectCreate, type ProjectUpdate } from '$lib/api';
	import { conversationsApi, type Conversation } from '$lib/api/conversations';
	import ProjectDialog from '$lib/components/projects/ProjectDialog.svelte';
	import AssignDocumentsDialog from '$lib/components/projects/AssignDocumentsDialog.svelte';

	interface Props {
		data: { projectId: string };
	}

	let { data }: Props = $props();

	// State
	let project = $state<ProjectDetail | null>(null);
	let documents = $state<Document[]>([]);
	let conversations = $state<Conversation[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	// Dialog states
	let showEditDialog = $state(false);
	let showAssignDialog = $state(false);
	let showDeleteConfirm = $state(false);
	let deleting = $state(false);

	// Derived
	let documentIds = $derived(documents.map((d) => d.id));

	onMount(async () => {
		await loadProject();
	});

	async function loadProject() {
		loading = true;
		error = null;

		try {
			const [projectData, documentsData] = await Promise.all([
				projectsApi.get(data.projectId),
				projectsApi.getDocuments(data.projectId)
			]);

			project = projectData;
			documents = documentsData;

			// TODO: Load conversations for this project when API is available
			// For now, just set empty array
			conversations = [];
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load project';
		} finally {
			loading = false;
		}
	}

	async function handleEditSave(data: ProjectCreate | ProjectUpdate) {
		if (!project) return;

		try {
			await projectsApi.update(project.id, data as ProjectUpdate);
			project = { ...project, name: data.name ?? project.name, description: data.description ?? project.description };
			showEditDialog = false;
		} catch (e) {
			console.error('Failed to update project:', e);
		}
	}

	async function handleDelete() {
		if (!project || deleting) return;

		deleting = true;
		try {
			await projectsApi.delete(project.id);
			goto('/chat');
		} catch (e) {
			console.error('Failed to delete project:', e);
		} finally {
			deleting = false;
		}
	}

	async function handleAssignDocuments(documentIds: string[]) {
		if (!project) return;

		await projectsApi.assignDocuments(project.id, documentIds);
		// Reload documents
		documents = await projectsApi.getDocuments(project.id);
		// Update project counts
		project = await projectsApi.get(project.id);
	}

	async function handleRemoveDocument(docId: string) {
		if (!project) return;

		try {
			await projectsApi.removeDocuments(project.id, [docId]);
			documents = documents.filter((d) => d.id !== docId);
			project = { ...project, document_count: project.document_count - 1 };
		} catch (e) {
			console.error('Failed to remove document:', e);
		}
	}

	function formatDate(dateString: string): string {
		return new Date(dateString).toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'short',
			day: 'numeric'
		});
	}

	function formatFileSize(bytes: number): string {
		if (bytes < 1024) return `${bytes} B`;
		if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
		return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
	}
</script>

<svelte:head>
	<title>{project?.name || 'Project'} | RAG Agent</title>
</svelte:head>

<div class="flex h-full flex-col">
	<!-- Header -->
	<div class="border-b bg-background p-4">
		<div class="flex items-center justify-between">
			<div class="flex items-center gap-3">
				<Button variant="ghost" size="icon" onclick={() => goto('/chat')}>
					<ArrowLeft class="size-4" />
				</Button>

				{#if loading}
					<div class="h-6 w-32 animate-pulse rounded bg-muted"></div>
				{:else if project}
					<div class="flex items-center gap-2">
						<FolderOpen class="size-5" />
						<h1 class="text-lg font-semibold">{project.name}</h1>
					</div>
				{/if}
			</div>

			{#if project && !loading}
				<div class="flex items-center gap-2">
					<Button variant="outline" size="sm" onclick={() => (showEditDialog = true)}>
						<Pencil class="mr-2 size-3.5" />
						Edit
					</Button>

					{#if showDeleteConfirm}
						<div class="flex items-center gap-1">
							<Button
								variant="destructive"
								size="sm"
								onclick={handleDelete}
								disabled={deleting}
							>
								{deleting ? 'Deleting...' : 'Confirm Delete'}
							</Button>
							<Button
								variant="outline"
								size="sm"
								onclick={() => (showDeleteConfirm = false)}
							>
								Cancel
							</Button>
						</div>
					{:else}
						<Button
							variant="outline"
							size="sm"
							onclick={() => (showDeleteConfirm = true)}
							class="text-destructive hover:bg-destructive hover:text-destructive-foreground"
						>
							<Trash2 class="mr-2 size-3.5" />
							Delete
						</Button>
					{/if}
				</div>
			{/if}
		</div>

		<!-- Project info -->
		{#if project && !loading}
			<div class="mt-3 flex items-center gap-4 text-sm text-muted-foreground">
				{#if project.description}
					<p class="max-w-md truncate">{project.description}</p>
					<span class="text-muted-foreground/50">|</span>
				{/if}
				<span>Created {formatDate(project.created_at)}</span>
			</div>

			<!-- Stats -->
			<div class="mt-3 flex items-center gap-4">
				<Badge variant="secondary" class="gap-1.5">
					<FileText class="size-3" />
					{project.document_count} Documents
				</Badge>
				<Badge variant="secondary" class="gap-1.5">
					<MessageSquare class="size-3" />
					{project.conversation_count} Conversations
				</Badge>
			</div>
		{/if}
	</div>

	<!-- Content -->
	<div class="flex-1 overflow-auto p-4">
		{#if loading}
			<div class="flex items-center justify-center py-12">
				<div class="size-8 animate-spin rounded-full border-4 border-muted border-t-primary"></div>
			</div>
		{:else if error}
			<div class="rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-center">
				<p class="text-destructive">{error}</p>
				<Button variant="outline" class="mt-4" onclick={loadProject}>
					Try Again
				</Button>
			</div>
		{:else if project}
			<div class="mx-auto max-w-4xl">
				<Tabs.Root value="documents">
					<Tabs.List class="grid w-full grid-cols-2">
						<Tabs.Trigger value="documents">
							<FileText class="mr-2 size-4" />
							Documents ({documents.length})
						</Tabs.Trigger>
						<Tabs.Trigger value="conversations">
							<MessageSquare class="mr-2 size-4" />
							Conversations ({conversations.length})
						</Tabs.Trigger>
					</Tabs.List>

					<!-- Documents Tab -->
					<Tabs.Content value="documents" class="mt-4">
						<div class="mb-4 flex items-center justify-between">
							<p class="text-sm text-muted-foreground">
								Documents assigned to this project will be used for RAG when chatting.
							</p>
							<Button size="sm" onclick={() => (showAssignDialog = true)}>
								<Plus class="mr-2 size-3.5" />
								Assign Documents
							</Button>
						</div>

						{#if documents.length === 0}
							<div class="rounded-lg border border-dashed p-8 text-center">
								<FileText class="mx-auto size-10 text-muted-foreground/50" />
								<h3 class="mt-4 font-medium">No documents assigned</h3>
								<p class="mt-1 text-sm text-muted-foreground">
									Assign documents to this project to use them with RAG.
								</p>
								<Button class="mt-4" onclick={() => (showAssignDialog = true)}>
									<Plus class="mr-2 size-4" />
									Assign Documents
								</Button>
							</div>
						{:else}
							<div class="space-y-2">
								{#each documents as doc (doc.id)}
									<div
										class="flex items-center justify-between rounded-lg border bg-card p-3"
									>
										<div class="flex items-center gap-3">
											<div
												class="flex size-10 items-center justify-center rounded-lg bg-muted"
											>
												<FileText class="size-5 text-muted-foreground" />
											</div>
											<div>
												<p class="font-medium">{doc.filename}</p>
												<p class="text-xs text-muted-foreground">
													{formatFileSize(doc.file_size)}
													{#if doc.chunk_count > 0}
														&bull; {doc.chunk_count} chunks
													{/if}
												</p>
											</div>
										</div>
										<Button
											variant="ghost"
											size="icon-sm"
											onclick={() => handleRemoveDocument(doc.id)}
											title="Remove from project"
										>
											<X class="size-4" />
										</Button>
									</div>
								{/each}
							</div>
						{/if}
					</Tabs.Content>

					<!-- Conversations Tab -->
					<Tabs.Content value="conversations" class="mt-4">
						{#if conversations.length === 0}
							<div class="rounded-lg border border-dashed p-8 text-center">
								<MessageSquare class="mx-auto size-10 text-muted-foreground/50" />
								<h3 class="mt-4 font-medium">No conversations yet</h3>
								<p class="mt-1 text-sm text-muted-foreground">
									Start a chat with this project selected to create conversations.
								</p>
								<Button class="mt-4" onclick={() => goto('/chat')}>
									<MessageSquare class="mr-2 size-4" />
									Start Chat
								</Button>
							</div>
						{:else}
							<div class="space-y-2">
								{#each conversations as conv (conv.id)}
									<a
										href={`/chat/${conv.id}`}
										class="flex items-center justify-between rounded-lg border bg-card p-3 transition-colors hover:bg-muted/50"
									>
										<div>
											<p class="font-medium">
												{conv.title || 'Untitled conversation'}
											</p>
											<p class="text-xs text-muted-foreground">
												{conv.message_count} messages &bull; {formatDate(conv.updated_at)}
											</p>
										</div>
									</a>
								{/each}
							</div>
						{/if}
					</Tabs.Content>
				</Tabs.Root>
			</div>
		{/if}
	</div>
</div>

<!-- Edit Dialog -->
<ProjectDialog
	bind:open={showEditDialog}
	project={project}
	onSave={handleEditSave}
/>

<!-- Assign Documents Dialog -->
<AssignDocumentsDialog
	bind:open={showAssignDialog}
	projectId={data.projectId}
	existingDocumentIds={documentIds}
	onAssign={handleAssignDocuments}
/>
