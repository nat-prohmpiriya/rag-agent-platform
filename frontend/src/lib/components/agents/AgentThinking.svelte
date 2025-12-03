<script lang="ts">
	import { Loader2, CheckCircle2, XCircle, Brain, Wrench, FileText } from 'lucide-svelte';

	export interface ThinkingStep {
		type: 'thinking' | 'tool_call' | 'tool_result';
		content: string;
		toolName?: string;
		status?: 'running' | 'done' | 'error';
	}

	interface Props {
		steps: ThinkingStep[];
	}

	let { steps }: Props = $props();

	function getStepIcon(step: ThinkingStep) {
		switch (step.type) {
			case 'thinking':
				return Brain;
			case 'tool_call':
				return Wrench;
			case 'tool_result':
				return FileText;
			default:
				return Brain;
		}
	}

	function getStatusIcon(status?: string) {
		switch (status) {
			case 'running':
				return Loader2;
			case 'done':
				return CheckCircle2;
			case 'error':
				return XCircle;
			default:
				return null;
		}
	}

	function getStatusColor(status?: string): string {
		switch (status) {
			case 'running':
				return 'text-blue-500';
			case 'done':
				return 'text-green-500';
			case 'error':
				return 'text-red-500';
			default:
				return 'text-muted-foreground';
		}
	}

	function getStepLabel(step: ThinkingStep): string {
		switch (step.type) {
			case 'thinking':
				return 'Thinking';
			case 'tool_call':
				return step.toolName ? `Calling ${step.toolName}` : 'Calling tool';
			case 'tool_result':
				return step.toolName ? `Result from ${step.toolName}` : 'Tool result';
			default:
				return '';
		}
	}
</script>

<div class="space-y-2">
	{#each steps as step, i}
		{@const StepIcon = getStepIcon(step)}
		{@const StatusIcon = getStatusIcon(step.status)}
		<div
			class="flex items-start gap-3 rounded-lg border bg-muted/30 p-3 text-sm"
		>
			<div class="flex items-center gap-2 shrink-0">
				<StepIcon class="size-4 text-muted-foreground" />
				{#if step.status && StatusIcon}
					<StatusIcon
						class="size-4 {getStatusColor(step.status)} {step.status === 'running'
							? 'animate-spin'
							: ''}"
					/>
				{/if}
			</div>
			<div class="flex-1 min-w-0">
				<div class="font-medium text-xs text-muted-foreground mb-1">
					{getStepLabel(step)}
				</div>
				<div class="text-foreground whitespace-pre-wrap break-words">
					{step.content}
				</div>
			</div>
		</div>
	{/each}
</div>
