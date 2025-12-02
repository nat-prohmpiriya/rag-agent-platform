<script lang="ts">
	import { goto } from '$app/navigation';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import { auth } from '$lib/stores';
	import { onMount } from 'svelte';

	// Redirect authenticated users to dashboard
	onMount(() => {
		if (auth.isAuthenticated) {
			goto('/dashboard');
		}
	});

	// Watch for auth changes
	$effect(() => {
		if (!auth.isLoading && auth.isAuthenticated) {
			goto('/dashboard');
		}
	});
</script>

<svelte:head>
	<title>RAG Agent Platform - AI-Powered Document Intelligence</title>
</svelte:head>

{#if auth.isLoading}
	<div class="min-h-screen flex items-center justify-center bg-background">
		<div class="flex flex-col items-center gap-4">
			<svg class="h-8 w-8 animate-spin text-primary" viewBox="0 0 24 24">
				<circle
					class="opacity-25"
					cx="12"
					cy="12"
					r="10"
					stroke="currentColor"
					stroke-width="4"
					fill="none"
				/>
				<path
					class="opacity-75"
					fill="currentColor"
					d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
				/>
			</svg>
			<p class="text-muted-foreground">Loading...</p>
		</div>
	</div>
{:else}
	<!-- Landing page -->
	<div class="min-h-screen bg-background">
		<header class="border-b">
			<div class="container mx-auto px-4 py-4 flex items-center justify-between">
				<div class="flex items-center gap-2">
					<svg class="h-6 w-6 text-primary" viewBox="0 0 24 24" fill="currentColor">
						<path
							d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
							stroke="currentColor"
							stroke-width="2"
							fill="none"
						/>
					</svg>
					<span class="font-semibold text-lg">RAG Agent Platform</span>
				</div>
				<div class="flex items-center gap-2">
					<Button variant="ghost" href="/login">Login</Button>
					<Button href="/register">Get Started</Button>
				</div>
			</div>
		</header>

		<main class="container mx-auto px-4 py-16">
			<!-- Hero Section -->
			<div class="max-w-3xl mx-auto text-center space-y-8">
				<h1 class="text-4xl md:text-6xl font-bold tracking-tight">
					AI-Powered Document Intelligence
				</h1>
				<p class="text-xl text-muted-foreground">
					Chat with your documents, query databases naturally, and let AI agents handle
					complex tasks - all with enterprise-grade privacy protection.
				</p>
				<div class="flex justify-center gap-4">
					<Button size="lg" href="/register">Start Free Trial</Button>
					<Button size="lg" variant="outline" href="/login">Sign In</Button>
				</div>
			</div>

			<!-- Features Section -->
			<div class="mt-24 grid gap-8 md:grid-cols-2 lg:grid-cols-4">
				<Card.Root>
					<Card.Header>
						<Card.Title class="flex items-center gap-2">
							<svg
								class="h-5 w-5 text-primary"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
							>
								<path
									d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
								/>
							</svg>
							RAG-Powered Chat
						</Card.Title>
					</Card.Header>
					<Card.Content>
						<p class="text-muted-foreground">
							Upload documents and ask questions. Get accurate answers with source citations.
						</p>
					</Card.Content>
				</Card.Root>

				<Card.Root>
					<Card.Header>
						<Card.Title class="flex items-center gap-2">
							<svg
								class="h-5 w-5 text-primary"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
							>
								<path
									d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"
								/>
							</svg>
							Text-to-SQL
						</Card.Title>
					</Card.Header>
					<Card.Content>
						<p class="text-muted-foreground">
							Query your databases using natural language. Review SQL before execution.
						</p>
					</Card.Content>
				</Card.Root>

				<Card.Root>
					<Card.Header>
						<Card.Title class="flex items-center gap-2">
							<svg
								class="h-5 w-5 text-primary"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
							>
								<path d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
							</svg>
							Privacy First
						</Card.Title>
					</Card.Header>
					<Card.Content>
						<p class="text-muted-foreground">
							Built-in PII protection ensures sensitive data never leaves your control.
						</p>
					</Card.Content>
				</Card.Root>

				<Card.Root>
					<Card.Header>
						<Card.Title class="flex items-center gap-2">
							<svg
								class="h-5 w-5 text-primary"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
							>
								<path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
							</svg>
							Multi-Agent
						</Card.Title>
					</Card.Header>
					<Card.Content>
						<p class="text-muted-foreground">
							Pre-built agents for HR, Legal, Finance, Research, and Mental Health domains.
						</p>
					</Card.Content>
				</Card.Root>
			</div>

			<!-- Tech Stack Section -->
			<div class="mt-24 text-center">
				<h2 class="text-2xl font-bold mb-8">Built with Modern Tech Stack</h2>
				<div class="flex flex-wrap justify-center gap-4">
					<span class="px-4 py-2 bg-muted rounded-full text-sm">SvelteKit</span>
					<span class="px-4 py-2 bg-muted rounded-full text-sm">FastAPI</span>
					<span class="px-4 py-2 bg-muted rounded-full text-sm">LiteLLM</span>
					<span class="px-4 py-2 bg-muted rounded-full text-sm">ChromaDB</span>
					<span class="px-4 py-2 bg-muted rounded-full text-sm">PostgreSQL</span>
					<span class="px-4 py-2 bg-muted rounded-full text-sm">Presidio</span>
				</div>
			</div>

			<!-- CTA Section -->
			<div class="mt-24 text-center">
				<Card.Root class="max-w-xl mx-auto">
					<Card.Header>
						<Card.Title>Ready to get started?</Card.Title>
						<Card.Description>
							Create an account and start chatting with your documents today.
						</Card.Description>
					</Card.Header>
					<Card.Content>
						<div class="flex justify-center gap-4">
							<Button href="/register">Create Account</Button>
							<Button variant="outline" href="/login">Sign In</Button>
						</div>
					</Card.Content>
				</Card.Root>
			</div>
		</main>

		<!-- Footer -->
		<footer class="border-t mt-24">
			<div class="container mx-auto px-4 py-8 text-center text-muted-foreground text-sm">
				<p>RAG Agent Platform - Portfolio Project</p>
			</div>
		</footer>
	</div>
{/if}
