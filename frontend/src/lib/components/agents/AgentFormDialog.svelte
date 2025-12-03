<script lang="ts">
	import * as Dialog from '$lib/components/ui/dialog';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Textarea } from '$lib/components/ui/textarea';
	import { Label } from '$lib/components/ui/label';
	import { Switch } from '$lib/components/ui/switch';
	import { Badge } from '$lib/components/ui/badge';
	import type { AgentInfo, AgentCreate, AgentUpdate } from '$lib/api';

	let {
		open = $bindable(false),
		mode = 'create',
		agent = null,
		onSave
	} = $props<{
		open: boolean;
		mode: 'create' | 'edit';
		agent: AgentInfo | null;
		onSave: (data: AgentCreate | AgentUpdate) => Promise<void>;
	}>();

	// Form state
	let name = $state('');
	let slug = $state('');
	let description = $state('');
	let systemPrompt = $state('');
	let icon = $state('');
	let isActive = $state(true);
	let toolInput = $state('');
	let tools = $state<string[]>([]);
	let saving = $state(false);
	let error = $state<string | null>(null);

	// Available tools
	const availableTools = ['rag_search', 'calculator', 'web_search'];

	// Derived states
	let isEdit = $derived(mode === 'edit');
	let title = $derived(isEdit ? 'Edit Agent' : 'Create Agent');
	let submitLabel = $derived(isEdit ? 'Save Changes' : 'Create Agent');
	let isValid = $derived(
		name.trim().length > 0 &&
		name.trim().length <= 100 &&
		slug.trim().length > 0 &&
		slug.trim().length <= 50 &&
		/^[a-z0-9-]+$/.test(slug.trim())
	);

	// Reset form when dialog opens or agent changes
	$effect(() => {
		if (open) {
			if (agent && isEdit) {
				name = agent.name;
				slug = agent.slug;
				description = agent.description || '';
				systemPrompt = (agent as any).system_prompt || '';
				icon = agent.icon || '';
				isActive = agent.is_active;
				tools = [...(agent.tools || [])];
			} else {
				name = '';
				slug = '';
				description = '';
				systemPrompt = '';
				icon = '';
				isActive = true;
				tools = [];
			}
			error = null;
		}
	});

	// Auto-generate slug from name
	function generateSlug(value: string): string {
		return value
			.toLowerCase()
			.replace(/\s+/g, '-')
			.replace(/[^a-z0-9-]/g, '')
			.slice(0, 50);
	}

	function handleNameChange(e: Event) {
		const input = e.target as HTMLInputElement;
		name = input.value;
		if (!isEdit && !slug) {
			slug = generateSlug(name);
		}
	}

	function addTool(tool: string) {
		if (!tools.includes(tool)) {
			tools = [...tools, tool];
		}
	}

	function removeTool(tool: string) {
		tools = tools.filter(t => t !== tool);
	}

	async function handleSubmit() {
		if (!isValid || saving) return;

		saving = true;
		error = null;

		try {
			const data: AgentCreate | AgentUpdate = {
				name: name.trim(),
				slug: slug.trim(),
				description: description.trim() || undefined,
				system_prompt: systemPrompt.trim() || undefined,
				icon: icon.trim() || undefined,
				is_active: isActive,
				tools: tools.length > 0 ? tools : undefined,
			};

			await onSave(data);
			open = false;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to save agent';
		} finally {
			saving = false;
		}
	}

	function handleClose() {
		if (!saving) {
			open = false;
		}
	}
</script>

<Dialog.Root bind:open onOpenChange={(isOpen) => !isOpen && handleClose()}>
	<Dialog.Portal>
		<Dialog.Overlay />
		<Dialog.Content class="sm:max-w-lg max-h-[90vh] overflow-y-auto">
			<Dialog.Header>
				<Dialog.Title>{title}</Dialog.Title>
				<Dialog.Description>
					{isEdit ? 'Update the agent configuration below.' : 'Create a custom agent with your own settings.'}
				</Dialog.Description>
			</Dialog.Header>

			<form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }} class="space-y-4">
				<!-- Name -->
				<div class="space-y-2">
					<Label for="agent-name">Name *</Label>
					<Input
						id="agent-name"
						value={name}
						oninput={handleNameChange}
						placeholder="My Research Agent"
						maxlength={100}
						disabled={saving}
					/>
				</div>

				<!-- Slug -->
				<div class="space-y-2">
					<Label for="agent-slug">Slug *</Label>
					<Input
						id="agent-slug"
						bind:value={slug}
						placeholder="my-research-agent"
						maxlength={50}
						disabled={saving || isEdit}
						class={slug.length > 0 && !/^[a-z0-9-]+$/.test(slug) ? 'border-destructive' : ''}
					/>
					<p class="text-xs text-muted-foreground">
						Lowercase letters, numbers, and hyphens only
					</p>
				</div>

				<!-- Description -->
				<div class="space-y-2">
					<Label for="agent-description">Description</Label>
					<Textarea
						id="agent-description"
						bind:value={description}
						placeholder="What this agent does..."
						rows={2}
						disabled={saving}
					/>
				</div>

				<!-- System Prompt -->
				<div class="space-y-2">
					<Label for="agent-prompt">System Prompt</Label>
					<Textarea
						id="agent-prompt"
						bind:value={systemPrompt}
						placeholder="You are a helpful assistant that..."
						rows={4}
						disabled={saving}
					/>
					<p class="text-xs text-muted-foreground">
						Instructions that define the agent's behavior
					</p>
				</div>

				<!-- Icon -->
				<div class="space-y-2">
					<Label for="agent-icon">Icon</Label>
					<Input
						id="agent-icon"
						bind:value={icon}
						placeholder="robot, search, brain..."
						disabled={saving}
					/>
				</div>

				<!-- Tools -->
				<div class="space-y-2">
					<Label>Tools</Label>
					<div class="flex flex-wrap gap-2 mb-2">
						{#each tools as tool}
							<Badge variant="secondary" class="gap-1">
								{tool}
								<button
									type="button"
									onclick={() => removeTool(tool)}
									class="ml-1 hover:text-destructive"
									disabled={saving}
								>
									&times;
								</button>
							</Badge>
						{/each}
					</div>
					<div class="flex flex-wrap gap-2">
						{#each availableTools.filter(t => !tools.includes(t)) as tool}
							<Button
								type="button"
								variant="outline"
								size="sm"
								onclick={() => addTool(tool)}
								disabled={saving}
							>
								+ {tool}
							</Button>
						{/each}
					</div>
				</div>

				<!-- Active -->
				<div class="flex items-center justify-between">
					<Label for="agent-active">Active</Label>
					<Switch
						id="agent-active"
						checked={isActive}
						onCheckedChange={(checked) => isActive = checked}
						disabled={saving}
					/>
				</div>

				{#if error}
					<p class="text-sm text-destructive">{error}</p>
				{/if}

				<Dialog.Footer>
					<Button type="button" variant="outline" onclick={handleClose} disabled={saving}>
						Cancel
					</Button>
					<Button type="submit" disabled={!isValid || saving}>
						{#if saving}
							Saving...
						{:else}
							{submitLabel}
						{/if}
					</Button>
				</Dialog.Footer>
			</form>
		</Dialog.Content>
	</Dialog.Portal>
</Dialog.Root>
