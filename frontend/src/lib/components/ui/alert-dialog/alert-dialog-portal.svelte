<script lang="ts">
	import { AlertDialog as AlertDialogPrimitive } from "bits-ui";
	import type { Snippet } from "svelte";
	import { type WithoutChildrenOrChild } from "$lib/utils.js";

	let {
		children,
		...restProps
	}: WithoutChildrenOrChild<AlertDialogPrimitive.PortalProps> & {
		children: Snippet;
	} = $props();
</script>

<AlertDialogPrimitive.Portal {...restProps}>
	{@render children?.()}
</AlertDialogPrimitive.Portal>
