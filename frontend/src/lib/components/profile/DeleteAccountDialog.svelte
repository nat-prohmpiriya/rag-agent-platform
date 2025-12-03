<script lang="ts">
	import * as AlertDialog from '$lib/components/ui/alert-dialog';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { profileApi, removeStoredToken } from '$lib/api';
	import { auth } from '$lib/stores';
	import { toast } from 'svelte-sonner';
	import { goto } from '$app/navigation';
	import { AlertTriangle, Eye, EyeOff } from 'lucide-svelte';

	let {
		open = $bindable(false)
	} = $props<{
		open: boolean;
	}>();

	let password = $state('');
	let confirmation = $state('');
	let deleting = $state(false);
	let error = $state<string | null>(null);
	let showPassword = $state(false);

	// Validation
	let isValid = $derived(
		password.length > 0 &&
		confirmation === 'DELETE'
	);

	// Reset form when dialog opens
	$effect(() => {
		if (open) {
			password = '';
			confirmation = '';
			showPassword = false;
			error = null;
		}
	});

	async function handleDelete() {
		if (!isValid || deleting) return;

		deleting = true;
		error = null;

		try {
			await profileApi.deleteAccount({
				password,
				confirmation
			});

			toast.success('Account deleted successfully');

			// Clear tokens and redirect
			removeStoredToken();
			auth.user = null;
			await goto('/login');
		} catch (e) {
			const message = e instanceof Error ? e.message : 'Failed to delete account';
			error = message;
			toast.error(message);
		} finally {
			deleting = false;
		}
	}

	function handleClose() {
		if (!deleting) {
			open = false;
		}
	}
</script>

<AlertDialog.Root bind:open onOpenChange={(isOpen) => !isOpen && handleClose()}>
	<AlertDialog.Portal>
		<AlertDialog.Overlay />
		<AlertDialog.Content class="sm:max-w-md">
			<AlertDialog.Header>
				<AlertDialog.Title class="flex items-center gap-2 text-destructive">
					<AlertTriangle class="size-5" />
					Delete Account
				</AlertDialog.Title>
				<AlertDialog.Description>
					<span class="font-semibold text-destructive">This action cannot be undone.</span>
				</AlertDialog.Description>
			</AlertDialog.Header>

			<div class="space-y-4">
				<!-- Warning Message -->
				<div class="rounded-lg border border-destructive/50 bg-destructive/10 p-4">
					<p class="text-sm font-medium text-destructive mb-2">Deleting your account will:</p>
					<ul class="text-sm text-muted-foreground space-y-1 list-disc list-inside">
						<li>Permanently remove all your conversations</li>
						<li>Delete all uploaded documents</li>
						<li>Remove all custom agents you created</li>
						<li>Revoke access to all projects</li>
					</ul>
				</div>

				<!-- Password Field -->
				<div class="space-y-2">
					<Label for="delete-password">Enter your password to confirm</Label>
					<div class="relative">
						<Input
							id="delete-password"
							type={showPassword ? 'text' : 'password'}
							bind:value={password}
							placeholder="Your password"
							disabled={deleting}
							class="pr-10"
						/>
						<button
							type="button"
							class="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
							onclick={() => showPassword = !showPassword}
						>
							{#if showPassword}
								<EyeOff class="size-4" />
							{:else}
								<Eye class="size-4" />
							{/if}
						</button>
					</div>
				</div>

				<!-- Confirmation Field -->
				<div class="space-y-2">
					<Label for="delete-confirmation">
						Type <span class="font-mono font-semibold text-destructive">DELETE</span> to confirm
					</Label>
					<Input
						id="delete-confirmation"
						type="text"
						bind:value={confirmation}
						placeholder="Type DELETE"
						disabled={deleting}
						class={confirmation.length > 0 && confirmation !== 'DELETE' ? 'border-destructive' : ''}
					/>
					{#if confirmation.length > 0 && confirmation !== 'DELETE'}
						<p class="text-xs text-destructive">Please type DELETE exactly</p>
					{/if}
				</div>

				{#if error}
					<p class="text-sm text-destructive">{error}</p>
				{/if}
			</div>

			<AlertDialog.Footer class="mt-4">
				<AlertDialog.Cancel disabled={deleting}>
					Cancel
				</AlertDialog.Cancel>
				<Button
					variant="destructive"
					onclick={handleDelete}
					disabled={!isValid || deleting}
				>
					{#if deleting}
						Deleting...
					{:else}
						Delete My Account
					{/if}
				</Button>
			</AlertDialog.Footer>
		</AlertDialog.Content>
	</AlertDialog.Portal>
</AlertDialog.Root>
