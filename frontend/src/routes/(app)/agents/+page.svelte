<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { Bot, Plus } from 'lucide-svelte';
	import { agentStore } from '$lib/stores/agents.svelte';
	import { Button } from '$lib/components/ui/button';
	import AgentCard from '$lib/components/agents/AgentCard.svelte';
	import AgentFormDialog from '$lib/components/agents/AgentFormDialog.svelte';
	import * as AlertDialog from '$lib/components/ui/alert-dialog';
	import type { AgentInfo, AgentCreate, AgentUpdate } from '$lib/api';

	// Dialog states
	let formDialogOpen = $state(false);
	let formDialogMode = $state<'create' | 'edit'>('create');
	let selectedAgent = $state<AgentInfo | null>(null);

	// Delete confirmation
	let deleteDialogOpen = $state(false);
	let agentToDelete = $state<AgentInfo | null>(null);
	let deleting = $state(false);

	// Derived: separate system and user agents
	let systemAgents = $derived(
		agentStore.currentAgents.filter(a => a.source === 'system')
	);
	let userAgents = $derived(
		agentStore.currentAgents.filter(a => a.source === 'user')
	);

	onMount(() => {
		agentStore.initFromStorage();
		agentStore.fetchAgents();
	});

	function handleAgentClick(slug: string) {
		agentStore.selectAgent(slug);
		goto('/chat');
	}

	function openCreateDialog() {
		selectedAgent = null;
		formDialogMode = 'create';
		formDialogOpen = true;
	}

	function openEditDialog(agent: AgentInfo) {
		selectedAgent = agent;
		formDialogMode = 'edit';
		formDialogOpen = true;
	}

	function openDeleteDialog(agent: AgentInfo) {
		agentToDelete = agent;
		deleteDialogOpen = true;
	}

	async function handleSave(data: AgentCreate | AgentUpdate) {
		if (formDialogMode === 'create') {
			await agentStore.createAgent(data as AgentCreate);
		} else if (selectedAgent?.id) {
			await agentStore.updateAgent(selectedAgent.id, data as AgentUpdate);
		}
	}

	async function handleDelete() {
		if (!agentToDelete?.id) return;

		deleting = true;
		try {
			await agentStore.deleteAgent(agentToDelete.id);
			deleteDialogOpen = false;
			agentToDelete = null;
		} catch (e) {
			console.error('Failed to delete agent:', e);
		} finally {
			deleting = false;
		}
	}
</script>

<svelte:head>
	<title>Agents | RAG Agent</title>
</svelte:head>

<div class="flex h-full flex-col">
	<!-- Header -->
	<div class="border-b bg-background p-4">
		<div class="flex items-center justify-between">
			<div class="flex items-center gap-2">
				<Bot class="size-5" />
				<h1 class="text-lg font-semibold">Agents</h1>
				{#if agentStore.currentAgents.length > 0}
					<span class="text-sm text-muted-foreground">({agentStore.currentAgents.length})</span>
				{/if}
			</div>
			<Button onclick={openCreateDialog}>
				<Plus class="size-4 mr-2" />
				New Agent
			</Button>
		</div>
		<p class="mt-1 text-sm text-muted-foreground">
			Select an agent to start a specialized conversation
		</p>
	</div>

	<!-- Content -->
	<div class="flex-1 overflow-auto p-4">
		<div class="mx-auto max-w-4xl space-y-8">
			{#if agentStore.loading}
				<div class="flex items-center justify-center py-12">
					<div
						class="size-8 animate-spin rounded-full border-4 border-muted border-t-primary"
					></div>
				</div>
			{:else if agentStore.currentError}
				<div class="rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-center">
					<p class="text-destructive">{agentStore.currentError}</p>
				</div>
			{:else if agentStore.currentAgents.length === 0}
				<div class="rounded-lg border border-dashed flex flex-col items-center p-12">
					<Bot class="size-12 text-muted-foreground/50" />
					<h3 class="mt-4 text-lg font-medium">No agents available</h3>
					<p class="mt-1 text-sm text-muted-foreground">
						Create your first agent to get started.
					</p>
					<Button class="mt-4" onclick={openCreateDialog}>
						<Plus class="size-4 mr-2" />
						Create Agent
					</Button>
				</div>
			{:else}
				<!-- My Agents Section -->
				{#if userAgents.length > 0}
					<section>
						<h2 class="text-sm font-medium text-muted-foreground mb-4">My Agents</h2>
						<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
							{#each userAgents as agent (agent.slug)}
								<AgentCard
									{agent}
									selected={agentStore.currentSelectedSlug === agent.slug}
									onclick={() => handleAgentClick(agent.slug)}
									onEdit={() => openEditDialog(agent)}
									onDelete={() => openDeleteDialog(agent)}
								/>
							{/each}
						</div>
					</section>
				{/if}

				<!-- System Agents Section -->
				{#if systemAgents.length > 0}
					<section>
						<h2 class="text-sm font-medium text-muted-foreground mb-4">System Agents</h2>
						<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
							{#each systemAgents as agent (agent.slug)}
								<AgentCard
									{agent}
									selected={agentStore.currentSelectedSlug === agent.slug}
									onclick={() => handleAgentClick(agent.slug)}
								/>
							{/each}
						</div>
					</section>
				{/if}
			{/if}
		</div>
	</div>
</div>

<!-- Agent Form Dialog -->
<AgentFormDialog
	bind:open={formDialogOpen}
	mode={formDialogMode}
	agent={selectedAgent}
	onSave={handleSave}
/>

<!-- Delete Confirmation Dialog -->
<AlertDialog.Root bind:open={deleteDialogOpen}>
	<AlertDialog.Content>
		<AlertDialog.Header>
			<AlertDialog.Title>Delete Agent</AlertDialog.Title>
			<AlertDialog.Description>
				Are you sure you want to delete "{agentToDelete?.name}"? This action cannot be undone.
			</AlertDialog.Description>
		</AlertDialog.Header>
		<AlertDialog.Footer>
			<AlertDialog.Cancel disabled={deleting}>Cancel</AlertDialog.Cancel>
			<AlertDialog.Action
				class="bg-destructive text-destructive-foreground hover:bg-destructive/90"
				disabled={deleting}
				onclick={handleDelete}
			>
				{deleting ? 'Deleting...' : 'Delete'}
			</AlertDialog.Action>
		</AlertDialog.Footer>
	</AlertDialog.Content>
</AlertDialog.Root>
