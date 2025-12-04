<script lang="ts">
	import { onMount } from 'svelte';
	import * as Card from '$lib/components/ui/card';
	import * as Tabs from '$lib/components/ui/tabs';
	import { Badge } from '$lib/components/ui/badge';
	import { Button } from '$lib/components/ui/button';
	import { profileApi, type UserProfile, type UserStats, type UserUsage } from '$lib/api';
	import { User, Mail, Calendar, MessageSquare, FileText, Bot, Settings, Key, Trash2, Loader2 } from 'lucide-svelte';
	import EditProfileDialog from '$lib/components/profile/EditProfileDialog.svelte';
	import ChangePasswordDialog from '$lib/components/profile/ChangePasswordDialog.svelte';
	import DeleteAccountDialog from '$lib/components/profile/DeleteAccountDialog.svelte';
	import UsageTab from '$lib/components/profile/UsageTab.svelte';

	let profile = $state<UserProfile | null>(null);
	let stats = $state<UserStats | null>(null);
	let usage = $state<UserUsage | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let editDialogOpen = $state(false);
	let changePasswordDialogOpen = $state(false);
	let deleteAccountDialogOpen = $state(false);

	onMount(async () => {
		await loadData();
	});

	async function loadData() {
		loading = true;
		error = null;
		try {
			const [profileData, statsData, usageData] = await Promise.all([
				profileApi.getProfile(),
				profileApi.getStats(),
				profileApi.getUsage()
			]);
			profile = profileData;
			stats = statsData;
			usage = usageData;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load profile data';
		} finally {
			loading = false;
		}
	}

	function getInitials(profile: UserProfile): string {
		if (profile.first_name && profile.last_name) {
			return `${profile.first_name[0]}${profile.last_name[0]}`.toUpperCase();
		}
		if (profile.username) {
			return profile.username.slice(0, 2).toUpperCase();
		}
		return profile.email[0].toUpperCase();
	}

	function getDisplayName(profile: UserProfile): string {
		if (profile.first_name && profile.last_name) {
			return `${profile.first_name} ${profile.last_name}`;
		}
		return profile.username;
	}

	function formatDate(dateString: string): string {
		return new Date(dateString).toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'long',
			day: 'numeric'
		});
	}

	function getTierVariant(tier: string): 'default' | 'secondary' | 'outline' {
		switch (tier.toLowerCase()) {
			case 'premium':
			case 'pro':
				return 'default';
			case 'basic':
				return 'secondary';
			default:
				return 'outline';
		}
	}
</script>

<svelte:head>
	<title>Profile - RAG Agent Platform</title>
</svelte:head>

<div class="space-y-6 p-6">
	<!-- Page Header -->
	<div>
		<h1 class="text-3xl font-bold">Profile</h1>
		<p class="text-muted-foreground mt-2">
			Manage your account settings and preferences.
		</p>
	</div>

	{#if loading}
		<div class="flex items-center justify-center py-12">
			<Loader2 class="size-8 animate-spin text-muted-foreground" />
		</div>
	{:else if error}
		<Card.Root class="border-destructive">
			<Card.Content class="pt-6">
				<p class="text-destructive text-center">{error}</p>
				<div class="flex justify-center mt-4">
					<Button variant="outline" onclick={loadData}>Try Again</Button>
				</div>
			</Card.Content>
		</Card.Root>
	{:else if profile}
		<Tabs.Root value="profile" class="w-full">
			<Tabs.List class="mb-6">
				<Tabs.Trigger value="profile">Profile</Tabs.Trigger>
				<Tabs.Trigger value="usage">Usage</Tabs.Trigger>
			</Tabs.List>

			<Tabs.Content value="profile">
				<div class="grid gap-6 lg:grid-cols-3">
					<!-- User Info Card -->
					<Card.Root class="lg:col-span-2">
						<Card.Header>
							<Card.Title class="flex items-center gap-2">
								<User class="size-5" />
								User Information
							</Card.Title>
							<Card.Description>Your personal details and account info</Card.Description>
						</Card.Header>
						<Card.Content>
							<div class="flex flex-col sm:flex-row gap-6">
								<!-- Avatar -->
								<div class="flex-shrink-0">
									<div class="flex size-24 items-center justify-center rounded-full bg-primary text-primary-foreground text-3xl font-semibold">
										{getInitials(profile)}
									</div>
								</div>

								<!-- User Details -->
								<div class="flex-1 space-y-4">
									<div>
										<h3 class="text-xl font-semibold">{getDisplayName(profile)}</h3>
										<p class="text-muted-foreground">@{profile.username}</p>
									</div>

									<div class="grid gap-3 sm:grid-cols-2">
										<div class="flex items-center gap-2 text-sm">
											<Mail class="size-4 text-muted-foreground" />
											<span>{profile.email}</span>
										</div>
										<div class="flex items-center gap-2 text-sm">
											<Calendar class="size-4 text-muted-foreground" />
											<span>Member since {formatDate(profile.created_at)}</span>
										</div>
									</div>

									<div class="flex items-center gap-2">
										<Badge variant={getTierVariant(profile.tier)}>
											{profile.tier.charAt(0).toUpperCase() + profile.tier.slice(1)} Plan
										</Badge>
										{#if profile.is_active}
											<Badge variant="outline" class="border-green-500 text-green-600">Active</Badge>
										{:else}
											<Badge variant="destructive">Inactive</Badge>
										{/if}
									</div>
								</div>
							</div>
						</Card.Content>
						<Card.Footer>
							<Button variant="outline" onclick={() => editDialogOpen = true}>
								<Settings class="size-4 mr-2" />
								Edit Profile
							</Button>
						</Card.Footer>
					</Card.Root>

					<!-- Quick Stats Card -->
					<Card.Root>
						<Card.Header>
							<Card.Title>Quick Stats</Card.Title>
							<Card.Description>Your platform activity overview</Card.Description>
						</Card.Header>
						<Card.Content>
							{#if stats}
								<div class="space-y-4">
									<div class="flex items-center justify-between p-3 rounded-lg bg-muted/50">
										<div class="flex items-center gap-3">
											<MessageSquare class="size-5 text-muted-foreground" />
											<span class="text-sm">Conversations</span>
										</div>
										<span class="text-lg font-semibold">{stats.conversations_count}</span>
									</div>

									<div class="flex items-center justify-between p-3 rounded-lg bg-muted/50">
										<div class="flex items-center gap-3">
											<FileText class="size-5 text-muted-foreground" />
											<span class="text-sm">Documents</span>
										</div>
										<span class="text-lg font-semibold">{stats.documents_count}</span>
									</div>

									<div class="flex items-center justify-between p-3 rounded-lg bg-muted/50">
										<div class="flex items-center gap-3">
											<Bot class="size-5 text-muted-foreground" />
											<span class="text-sm">Custom Agents</span>
										</div>
										<span class="text-lg font-semibold">{stats.agents_count}</span>
									</div>

									<div class="flex items-center justify-between p-3 rounded-lg bg-muted/50">
										<div class="flex items-center gap-3">
											<MessageSquare class="size-5 text-muted-foreground" />
											<span class="text-sm">Total Messages</span>
										</div>
										<span class="text-lg font-semibold">{stats.total_messages}</span>
									</div>
								</div>
							{/if}
						</Card.Content>
					</Card.Root>

					<!-- Account Management Card -->
					<Card.Root class="lg:col-span-3">
						<Card.Header>
							<Card.Title>Account Management</Card.Title>
							<Card.Description>Security and account settings</Card.Description>
						</Card.Header>
						<Card.Content>
							<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
								<Button variant="outline" class="justify-start h-auto py-4" onclick={() => changePasswordDialogOpen = true}>
									<Key class="size-5 mr-3" />
									<div class="text-left">
										<div class="font-medium">Change Password</div>
										<div class="text-xs text-muted-foreground">Update your password</div>
									</div>
								</Button>

								<Button variant="outline" class="justify-start h-auto py-4 border-destructive/50 hover:bg-destructive/10 hover:text-destructive" onclick={() => deleteAccountDialogOpen = true}>
									<Trash2 class="size-5 mr-3" />
									<div class="text-left">
										<div class="font-medium">Delete Account</div>
										<div class="text-xs text-muted-foreground">Permanently delete your account</div>
									</div>
								</Button>
							</div>
						</Card.Content>
					</Card.Root>
				</div>
			</Tabs.Content>

			<Tabs.Content value="usage">
				<UsageTab {usage} {stats} {loading} />
			</Tabs.Content>
		</Tabs.Root>

		<!-- Edit Profile Dialog -->
		<EditProfileDialog
			bind:open={editDialogOpen}
			user={profile}
			onSave={(updatedUser) => profile = updatedUser}
		/>

		<!-- Change Password Dialog -->
		<ChangePasswordDialog
			bind:open={changePasswordDialogOpen}
		/>

		<!-- Delete Account Dialog -->
		<DeleteAccountDialog
			bind:open={deleteAccountDialogOpen}
		/>
	{/if}
</div>
