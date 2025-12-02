<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import { auth } from '$lib/stores';
	import { getUserDisplayName } from '$lib/types';
</script>

<svelte:head>
	<title>Dashboard - RAG Agent Platform</title>
</svelte:head>

<div class="space-y-6 p-6">
	<!-- Welcome Header -->
	<div>
		<h1 class="text-3xl font-bold">
			Welcome back, {auth.user ? getUserDisplayName(auth.user) : ''}!
		</h1>
		<p class="text-muted-foreground mt-2">
			Start chatting with your documents or manage your projects.
		</p>
	</div>

	<!-- Quick Actions -->
	<div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
		<Card.Root class="hover:border-primary/50 transition-colors cursor-pointer">
			<Card.Header>
				<Card.Title class="flex items-center gap-2">
					<svg
						class="h-5 w-5"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
					>
						<path
							d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
						/>
					</svg>
					Start Chat
				</Card.Title>
				<Card.Description>Chat with AI using your documents</Card.Description>
			</Card.Header>
			<Card.Content>
				<Button class="w-full" href="/chat">Open Chat</Button>
			</Card.Content>
		</Card.Root>

		<Card.Root class="hover:border-primary/50 transition-colors cursor-pointer">
			<Card.Header>
				<Card.Title class="flex items-center gap-2">
					<svg
						class="h-5 w-5"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
					>
						<path
							d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
						/>
					</svg>
					Documents
				</Card.Title>
				<Card.Description>Upload and manage your documents</Card.Description>
			</Card.Header>
			<Card.Content>
				<Button variant="outline" class="w-full" href="/documents">Manage Documents</Button>
			</Card.Content>
		</Card.Root>

		<Card.Root class="hover:border-primary/50 transition-colors cursor-pointer">
			<Card.Header>
				<Card.Title class="flex items-center gap-2">
					<svg
						class="h-5 w-5"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
					>
						<path
							d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"
						/>
					</svg>
					SQL Query
				</Card.Title>
				<Card.Description>Query your database with natural language</Card.Description>
			</Card.Header>
			<Card.Content>
				<Button variant="outline" class="w-full" href="/sql">Query Database</Button>
			</Card.Content>
		</Card.Root>
	</div>

	<!-- Recent Conversations -->
	<Card.Root>
		<Card.Header>
			<Card.Title>Recent Conversations</Card.Title>
			<Card.Description>Continue where you left off</Card.Description>
		</Card.Header>
		<Card.Content>
			<p class="text-sm text-muted-foreground py-8 text-center">
				No recent conversations. Start a new chat to begin!
			</p>
		</Card.Content>
	</Card.Root>
</div>
