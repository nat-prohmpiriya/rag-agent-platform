<script lang="ts">
	import type { HTMLAttributes } from "svelte/elements";
	import { cn } from "$lib/utils.js";
	import type { Snippet } from "svelte";

	let {
		class: className,
		children,
		...restProps
	}: HTMLAttributes<HTMLDivElement> & {
		children: Snippet;
	} = $props();
</script>

<div
	class={cn("flex flex-col gap-2 text-center sm:text-start", className)}
	{...restProps}
>
	{@render children?.()}
</div>
