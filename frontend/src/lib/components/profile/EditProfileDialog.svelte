<script lang="ts">
	import * as Dialog from '$lib/components/ui/dialog';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { profileApi, type UserProfile, type UserUpdate } from '$lib/api';
	import { toast } from 'svelte-sonner';

	let {
		open = $bindable(false),
		user,
		onSave
	} = $props<{
		open: boolean;
		user: UserProfile;
		onSave: (updatedUser: UserProfile) => void;
	}>();

	let firstName = $state('');
	let lastName = $state('');
	let username = $state('');
	let saving = $state(false);
	let error = $state<string | null>(null);

	// Validation
	let usernameError = $derived(() => {
		if (username.length === 0) return null;
		if (username.length < 3) return 'Username must be at least 3 characters';
		if (username.length > 50) return 'Username must be at most 50 characters';
		if (!/^[a-zA-Z0-9_]+$/.test(username)) return 'Username can only contain letters, numbers, and underscores';
		return null;
	});

	let isValid = $derived(
		username.trim().length >= 3 &&
		username.trim().length <= 50 &&
		/^[a-zA-Z0-9_]+$/.test(username.trim())
	);

	// Reset form when dialog opens
	$effect(() => {
		if (open && user) {
			firstName = user.first_name || '';
			lastName = user.last_name || '';
			username = user.username;
			error = null;
		}
	});

	async function handleSubmit() {
		if (!isValid || saving) return;

		saving = true;
		error = null;

		try {
			const data: UserUpdate = {
				username: username.trim(),
				first_name: firstName.trim() || undefined,
				last_name: lastName.trim() || undefined
			};

			const updatedUser = await profileApi.updateProfile(data);
			toast.success('Profile updated successfully');
			onSave(updatedUser);
			open = false;
		} catch (e) {
			const message = e instanceof Error ? e.message : 'Failed to update profile';
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
				<Dialog.Title>Edit Profile</Dialog.Title>
				<Dialog.Description>
					Update your personal information below.
				</Dialog.Description>
			</Dialog.Header>

			<form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }} class="space-y-4">
				<div class="grid gap-4 sm:grid-cols-2">
					<div class="space-y-2">
						<Label for="first-name">First Name</Label>
						<Input
							id="first-name"
							bind:value={firstName}
							placeholder="John"
							disabled={saving}
						/>
					</div>

					<div class="space-y-2">
						<Label for="last-name">Last Name</Label>
						<Input
							id="last-name"
							bind:value={lastName}
							placeholder="Doe"
							disabled={saving}
						/>
					</div>
				</div>

				<div class="space-y-2">
					<Label for="username">Username *</Label>
					<Input
						id="username"
						bind:value={username}
						placeholder="johndoe"
						maxlength={50}
						disabled={saving}
						class={usernameError() ? 'border-destructive' : ''}
					/>
					{#if usernameError()}
						<p class="text-xs text-destructive">{usernameError()}</p>
					{:else}
						<p class="text-xs text-muted-foreground">3-50 characters. Letters, numbers, and underscores only.</p>
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
							Saving...
						{:else}
							Save Changes
						{/if}
					</Button>
				</Dialog.Footer>
			</form>
		</Dialog.Content>
	</Dialog.Portal>
</Dialog.Root>
