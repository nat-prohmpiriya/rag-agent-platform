<script lang="ts">
	import { Image, Upload } from 'lucide-svelte';

	let images = $state<any[]>([]);
	let loading = $state(false);
</script>

<svelte:head>
	<title>Images | RAG Agent</title>
</svelte:head>

<div class="flex h-full flex-col">
	<!-- Header -->
	<div class="bg-background p-4">
		<div class="flex items-center justify-between">
			<div class="flex items-center gap-2">
				<Image class="size-5" />
				<h1 class="text-lg font-semibold">Images</h1>
				{#if images.length > 0}
					<span class="text-sm text-muted-foreground">({images.length})</span>
				{/if}
			</div>
		</div>
	</div>

	<!-- Content -->
	<div class="flex-1 overflow-auto p-4">
		<div class="mx-auto max-w-3xl space-y-6">
			{#if loading}
				<div class="flex items-center justify-center py-12">
					<div
						class="size-8 animate-spin rounded-full border-4 border-muted border-t-primary"
					></div>
				</div>
			{:else if images.length === 0}
				<div class="rounded-lg border border-dashed flex flex-col items-center p-12">
					<Image class="size-12 text-muted-foreground/50" />
					<h3 class="mt-4 text-lg font-medium">No images yet</h3>
					<p class="mt-1 text-sm text-muted-foreground text-center">
						Image generation and management coming soon.
					</p>
				</div>
			{:else}
				<div class="grid grid-cols-2 md:grid-cols-3 gap-4">
					{#each images as image (image.id)}
						<div class="aspect-square rounded-lg border overflow-hidden">
							<img
								src={image.url}
								alt={image.title}
								class="w-full h-full object-cover"
							/>
						</div>
					{/each}
				</div>
			{/if}
		</div>
	</div>
</div>
