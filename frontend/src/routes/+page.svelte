<script lang="ts">
	import { goto } from '$app/navigation';
	import { auth } from '$lib/stores';
	import { onMount } from 'svelte';
	import {
		Navbar,
		Hero,
		Features,
		HowItWorks,
		Pricing,
		TechStack,
		FAQ,
		FinalCTA,
		Footer
	} from '$lib/components/landing';

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
	<title>RAG Agent Platform - Build AI Agents That Know Your Data</title>
	<meta name="description" content="Create custom AI chatbots powered by your documents. Multi-model support, custom tools, and enterprise-grade privacy." />
</svelte:head>

{#if auth.isLoading}
	<div class="min-h-screen flex items-center justify-center bg-[#0a0a0b]">
		<div class="flex flex-col items-center gap-4">
			<svg class="h-8 w-8 animate-spin text-indigo-500" viewBox="0 0 24 24">
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
			<p class="text-gray-400">Loading...</p>
		</div>
	</div>
{:else}
	<div class="min-h-screen bg-[#0a0a0b]">
		<Navbar />
		<main>
			<Hero />
			<Features />
			<HowItWorks />
			<Pricing />
			<TechStack />
			<FAQ />
			<FinalCTA />
		</main>
		<Footer />
	</div>
{/if}
