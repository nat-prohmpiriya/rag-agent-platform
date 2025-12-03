<script lang="ts">
	import * as Dialog from '$lib/components/ui/dialog';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { profileApi } from '$lib/api';
	import { toast } from 'svelte-sonner';
	import { Eye, EyeOff } from 'lucide-svelte';

	let {
		open = $bindable(false),
		onSuccess
	} = $props<{
		open: boolean;
		onSuccess?: () => void;
	}>();

	let currentPassword = $state('');
	let newPassword = $state('');
	let confirmPassword = $state('');
	let saving = $state(false);
	let error = $state<string | null>(null);

	// Password visibility toggles
	let showCurrentPassword = $state(false);
	let showNewPassword = $state(false);
	let showConfirmPassword = $state(false);

	// Validation
	let newPasswordError = $derived(() => {
		if (newPassword.length === 0) return null;
		if (newPassword.length < 8) return 'Password must be at least 8 characters';
		return null;
	});

	let confirmPasswordError = $derived(() => {
		if (confirmPassword.length === 0) return null;
		if (confirmPassword !== newPassword) return 'Passwords do not match';
		return null;
	});

	let isValid = $derived(
		currentPassword.length > 0 &&
		newPassword.length >= 8 &&
		confirmPassword === newPassword
	);

	// Reset form when dialog opens
	$effect(() => {
		if (open) {
			currentPassword = '';
			newPassword = '';
			confirmPassword = '';
			showCurrentPassword = false;
			showNewPassword = false;
			showConfirmPassword = false;
			error = null;
		}
	});

	async function handleSubmit() {
		if (!isValid || saving) return;

		saving = true;
		error = null;

		try {
			await profileApi.changePassword({
				current_password: currentPassword,
				new_password: newPassword,
				confirm_password: confirmPassword
			});
			toast.success('Password changed successfully');
			onSuccess?.();
			open = false;
		} catch (e) {
			const message = e instanceof Error ? e.message : 'Failed to change password';
			error = message;
			toast.error(message);
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
		<Dialog.Content class="sm:max-w-md">
			<Dialog.Header>
				<Dialog.Title>Change Password</Dialog.Title>
				<Dialog.Description>
					Enter your current password and choose a new one.
				</Dialog.Description>
			</Dialog.Header>

			<form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }} class="space-y-4">
				<div class="space-y-2">
					<Label for="current-password">Current Password</Label>
					<div class="relative">
						<Input
							id="current-password"
							type={showCurrentPassword ? 'text' : 'password'}
							bind:value={currentPassword}
							placeholder="Enter current password"
							disabled={saving}
							class="pr-10"
						/>
						<button
							type="button"
							class="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
							onclick={() => showCurrentPassword = !showCurrentPassword}
						>
							{#if showCurrentPassword}
								<EyeOff class="size-4" />
							{:else}
								<Eye class="size-4" />
							{/if}
						</button>
					</div>
				</div>

				<div class="space-y-2">
					<Label for="new-password">New Password</Label>
					<div class="relative">
						<Input
							id="new-password"
							type={showNewPassword ? 'text' : 'password'}
							bind:value={newPassword}
							placeholder="Enter new password"
							disabled={saving}
							class="pr-10 {newPasswordError() ? 'border-destructive' : ''}"
						/>
						<button
							type="button"
							class="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
							onclick={() => showNewPassword = !showNewPassword}
						>
							{#if showNewPassword}
								<EyeOff class="size-4" />
							{:else}
								<Eye class="size-4" />
							{/if}
						</button>
					</div>
					{#if newPasswordError()}
						<p class="text-xs text-destructive">{newPasswordError()}</p>
					{:else}
						<p class="text-xs text-muted-foreground">Minimum 8 characters</p>
					{/if}
				</div>

				<div class="space-y-2">
					<Label for="confirm-password">Confirm New Password</Label>
					<div class="relative">
						<Input
							id="confirm-password"
							type={showConfirmPassword ? 'text' : 'password'}
							bind:value={confirmPassword}
							placeholder="Confirm new password"
							disabled={saving}
							class="pr-10 {confirmPasswordError() ? 'border-destructive' : ''}"
						/>
						<button
							type="button"
							class="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
							onclick={() => showConfirmPassword = !showConfirmPassword}
						>
							{#if showConfirmPassword}
								<EyeOff class="size-4" />
							{:else}
								<Eye class="size-4" />
							{/if}
						</button>
					</div>
					{#if confirmPasswordError()}
						<p class="text-xs text-destructive">{confirmPasswordError()}</p>
					{/if}
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
							Changing...
						{:else}
							Change Password
						{/if}
					</Button>
				</Dialog.Footer>
			</form>
		</Dialog.Content>
	</Dialog.Portal>
</Dialog.Root>
