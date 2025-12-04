<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { Button } from '$lib/components/ui/button';
	import { Badge } from '$lib/components/ui/badge';
	import { Skeleton } from '$lib/components/ui/skeleton';
	import * as Tabs from '$lib/components/ui/tabs';
	import { getPlans, createCheckout, type BillingPlan } from '$lib/api/billing';
	import {
		ArrowLeft,
		Check,
		Sparkles,
		Zap,
		FileText,
		Folder,
		Bot,
		MessageSquare,
		Cpu
	} from 'lucide-svelte';
	import { toast } from 'svelte-sonner';

	let plans = $state<BillingPlan[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let billingInterval = $state<'monthly' | 'yearly'>('monthly');
	let checkoutLoading = $state<string | null>(null);

	// Calculate yearly savings
	function getYearlySavings(plan: BillingPlan): number {
		if (!plan.price_yearly) return 0;
		const monthlyTotal = plan.price_monthly * 12;
		return Math.round(((monthlyTotal - plan.price_yearly) / monthlyTotal) * 100);
	}

	// Get price based on billing interval
	function getPrice(plan: BillingPlan): number {
		if (billingInterval === 'yearly' && plan.price_yearly) {
			return plan.price_yearly / 12;
		}
		return plan.price_monthly;
	}

	// Format currency
	function formatCurrency(amount: number): string {
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: 'USD',
			minimumFractionDigits: 0,
			maximumFractionDigits: 0
		}).format(amount);
	}

	// Format large numbers
	function formatNumber(num: number): string {
		if (num >= 1000000) {
			return `${(num / 1000000).toFixed(1)}M`;
		}
		if (num >= 1000) {
			return `${(num / 1000).toFixed(0)}K`;
		}
		return num.toString();
	}

	// Get plan features
	function getPlanFeatures(plan: BillingPlan): string[] {
		const features: string[] = [];

		// Primary metrics: requests/credits
		features.push(`${formatNumber(plan.requests_per_month)} requests/month`);
		features.push(`${formatNumber(plan.credits_per_month)} credits/month`);

		// Resources
		features.push(`${plan.max_agents} AI Agents`);
		features.push(`${plan.max_documents} Documents`);
		features.push(`${plan.max_projects} Projects`);

		if (plan.allowed_models.length > 0) {
			const modelCount = plan.allowed_models.length;
			features.push(`${modelCount} AI Model${modelCount > 1 ? 's' : ''}`);
		}

		// Add features from features object
		if (plan.features) {
			if (plan.features.priority_support) features.push('Priority Support');
			if (plan.features.api_access) features.push('API Access');
			if (plan.features.custom_tools) features.push('Custom Tools');
			if (plan.features.sso) features.push('SSO & SAML');
			if (plan.features.dedicated_support) features.push('Dedicated Support');
			if (plan.features.sla) features.push('SLA Guarantee');
		}

		return features;
	}

	// Handle checkout
	async function handleCheckout(plan: BillingPlan) {
		if (plan.plan_type === 'free') {
			goto('/register');
			return;
		}

		if (plan.plan_type === 'enterprise') {
			goto('/contact');
			return;
		}

		checkoutLoading = plan.id;

		try {
			const baseUrl = window.location.origin;
			const response = await createCheckout({
				plan_id: plan.id,
				billing_interval: billingInterval,
				success_url: `${baseUrl}/billing/success?session_id={CHECKOUT_SESSION_ID}`,
				cancel_url: `${baseUrl}/pricing`
			});

			// Redirect to Stripe checkout
			window.location.href = response.url;
		} catch (e) {
			toast.error(e instanceof Error ? e.message : 'Failed to create checkout session');
			checkoutLoading = null;
		}
	}

	// Get CTA button text
	function getCtaText(plan: BillingPlan): string {
		if (checkoutLoading === plan.id) return 'Loading...';
		if (plan.plan_type === 'free') return 'Get Started';
		if (plan.plan_type === 'enterprise') return 'Contact Sales';
		return 'Subscribe';
	}

	// Check if plan is popular
	function isPopular(plan: BillingPlan): boolean {
		return plan.plan_type === 'pro';
	}

	onMount(async () => {
		try {
			plans = await getPlans();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load plans';
		} finally {
			loading = false;
		}
	});
</script>

<svelte:head>
	<title>Pricing - RAG Agent Platform</title>
	<meta name="description" content="Choose the right plan for your AI needs. Start free and scale as you grow." />
</svelte:head>

<div class="min-h-screen bg-[#0a0a0b]">
	<!-- Header -->
	<div class="border-b border-white/10">
		<div class="container mx-auto px-4 py-6">
			<Button variant="ghost" href="/" class="text-gray-400 hover:text-white mb-4">
				<ArrowLeft class="h-4 w-4 mr-2" />
				Back to Home
			</Button>
			<h1 class="text-3xl md:text-4xl font-bold text-white">Pricing</h1>
			<p class="text-gray-400 mt-2">Simple, transparent pricing. Start free and scale as you grow.</p>
		</div>
	</div>

	<!-- Content -->
	<div class="container mx-auto px-4 py-12">
		<!-- Billing Toggle -->
		<div class="flex justify-center mb-12">
			<Tabs.Root value={billingInterval} onValueChange={(v) => (billingInterval = v as 'monthly' | 'yearly')}>
				<Tabs.List class="bg-white/5 border border-white/10">
					<Tabs.Trigger value="monthly" class="data-[state=active]:bg-indigo-600 data-[state=active]:text-white">
						Monthly
					</Tabs.Trigger>
					<Tabs.Trigger value="yearly" class="data-[state=active]:bg-indigo-600 data-[state=active]:text-white">
						Yearly
						<Badge variant="secondary" class="ml-2 bg-green-500/20 text-green-400 border-green-500/30">
							Save 20%
						</Badge>
					</Tabs.Trigger>
				</Tabs.List>
			</Tabs.Root>
		</div>

		<!-- Plans Grid -->
		{#if loading}
			<div class="grid gap-6 md:grid-cols-2 lg:grid-cols-4 max-w-7xl mx-auto">
				{#each Array(4) as _}
					<div class="p-6 rounded-2xl border border-white/10 bg-white/[0.02]">
						<Skeleton class="h-6 w-24 mb-4" />
						<Skeleton class="h-10 w-32 mb-2" />
						<Skeleton class="h-4 w-48 mb-6" />
						<div class="space-y-3 mb-8">
							{#each Array(6) as _}
								<Skeleton class="h-4 w-full" />
							{/each}
						</div>
						<Skeleton class="h-10 w-full" />
					</div>
				{/each}
			</div>
		{:else if error}
			<div class="text-center py-12">
				<p class="text-red-400 mb-4">{error}</p>
				<Button variant="outline" onclick={() => window.location.reload()}>
					Try Again
				</Button>
			</div>
		{:else if plans.length === 0}
			<div class="text-center py-12">
				<p class="text-gray-400">No plans available at the moment.</p>
			</div>
		{:else}
			<div class="grid gap-6 md:grid-cols-2 lg:grid-cols-4 max-w-7xl mx-auto">
				{#each plans as plan (plan.id)}
					<div
						class="relative p-6 rounded-2xl border transition-all duration-300
							{isPopular(plan)
								? 'border-indigo-500/50 bg-gradient-to-b from-indigo-500/10 to-transparent lg:scale-105'
								: 'border-white/10 bg-white/[0.02] hover:bg-white/[0.04] hover:border-white/20'}"
					>
						{#if isPopular(plan)}
							<div class="absolute -top-4 left-1/2 -translate-x-1/2">
								<div class="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 text-white text-xs font-medium">
									<Sparkles class="h-3 w-3" />
									Most Popular
								</div>
							</div>
						{/if}

						<!-- Plan Header -->
						<div class="mb-4">
							<h3 class="text-lg font-semibold text-white mb-2">{plan.display_name}</h3>
							<div class="flex items-baseline gap-1">
								{#if plan.plan_type === 'enterprise'}
									<span class="text-4xl font-bold text-white">Custom</span>
								{:else}
									<span class="text-4xl font-bold text-white">{formatCurrency(getPrice(plan))}</span>
									<span class="text-gray-500 text-sm">/month</span>
								{/if}
							</div>
							{#if billingInterval === 'yearly' && plan.price_yearly && plan.plan_type !== 'enterprise'}
								<p class="text-green-400 text-sm mt-1">
									{formatCurrency(plan.price_yearly)} billed yearly
									<span class="text-green-500">(Save {getYearlySavings(plan)}%)</span>
								</p>
							{/if}
							{#if plan.description}
								<p class="text-gray-400 text-sm mt-2">{plan.description}</p>
							{/if}
						</div>

						<!-- Features -->
						<ul class="space-y-2 mb-6">
							{#each getPlanFeatures(plan) as feature}
								<li class="flex items-center gap-2 text-sm text-gray-300">
									<Check class="h-3.5 w-3.5 text-indigo-400 flex-shrink-0" />
									{feature}
								</li>
							{/each}
						</ul>

						<!-- Models Badge -->
						{#if plan.allowed_models.length > 0}
							<div class="mb-4 pb-4 border-b border-white/10">
								<p class="text-xs text-gray-500 mb-2">Available Models</p>
								<div class="flex flex-wrap gap-1">
									{#each plan.allowed_models.slice(0, 3) as model}
										<Badge variant="outline" class="text-xs border-white/20 text-gray-400">
											{model.split('/').pop()}
										</Badge>
									{/each}
									{#if plan.allowed_models.length > 3}
										<Badge variant="outline" class="text-xs border-white/20 text-gray-400">
											+{plan.allowed_models.length - 3} more
										</Badge>
									{/if}
								</div>
							</div>
						{/if}

						<!-- CTA -->
						<Button
							onclick={() => handleCheckout(plan)}
							disabled={checkoutLoading !== null}
							variant={isPopular(plan) ? 'default' : 'outline'}
							class="w-full {isPopular(plan)
								? 'bg-indigo-600 hover:bg-indigo-700 text-white'
								: 'border-white/20 text-gray-300 hover:bg-white/5 hover:text-white'}"
						>
							{getCtaText(plan)}
						</Button>
					</div>
				{/each}
			</div>

			<!-- FAQ Section -->
			<div class="max-w-3xl mx-auto mt-20">
				<h2 class="text-2xl font-bold text-white text-center mb-8">Frequently Asked Questions</h2>
				<div class="space-y-4">
					<div class="p-6 rounded-2xl border border-white/10 bg-white/[0.02]">
						<h3 class="font-semibold text-white mb-2">Can I change plans later?</h3>
						<p class="text-gray-400 text-sm">
							Yes! You can upgrade or downgrade your plan at any time. When upgrading, you'll be charged the prorated difference. When downgrading, changes take effect at the end of your billing cycle.
						</p>
					</div>
					<div class="p-6 rounded-2xl border border-white/10 bg-white/[0.02]">
						<h3 class="font-semibold text-white mb-2">What payment methods do you accept?</h3>
						<p class="text-gray-400 text-sm">
							We accept all major credit cards (Visa, MasterCard, American Express) through our secure payment processor, Stripe.
						</p>
					</div>
					<div class="p-6 rounded-2xl border border-white/10 bg-white/[0.02]">
						<h3 class="font-semibold text-white mb-2">Is there a free trial?</h3>
						<p class="text-gray-400 text-sm">
							Our Free plan lets you try the platform with limited features. For Pro features, we offer a 14-day free trial so you can test everything before committing.
						</p>
					</div>
					<div class="p-6 rounded-2xl border border-white/10 bg-white/[0.02]">
						<h3 class="font-semibold text-white mb-2">What happens if I exceed my limits?</h3>
						<p class="text-gray-400 text-sm">
							We'll notify you when you're approaching your limits. You can upgrade your plan or wait until the next billing cycle for your limits to reset.
						</p>
					</div>
				</div>
			</div>
		{/if}
	</div>
</div>
