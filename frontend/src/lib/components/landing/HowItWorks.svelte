<script lang="ts">
  import { Upload, Bot, MessageSquare, Sparkles } from "lucide-svelte";

  const steps = [
    {
      step: "01",
      icon: Upload,
      title: "Upload Your Documents",
      description: "Drop your PDFs, docs, or text files. Our system automatically processes and indexes your content for AI retrieval.",
      color: "indigo"
    },
    {
      step: "02",
      icon: Bot,
      title: "Configure Your Agent",
      description: "Set up your AI agent's personality, knowledge scope, and behavior. Choose your preferred LLM model and customize responses.",
      color: "cyan"
    },
    {
      step: "03",
      icon: MessageSquare,
      title: "Start Chatting",
      description: "Ask questions naturally. Your agent searches through documents and provides accurate, contextual answers with source citations.",
      color: "purple"
    },
    {
      step: "04",
      icon: Sparkles,
      title: "Deploy & Scale",
      description: "Share your agent via API or embed in your app. Monitor usage, track performance, and scale as needed.",
      color: "pink"
    }
  ];

  const colorClasses: Record<string, { bg: string; text: string; gradient: string }> = {
    indigo: { bg: "bg-indigo-500/10", text: "text-indigo-400", gradient: "from-indigo-500" },
    cyan: { bg: "bg-cyan-500/10", text: "text-cyan-400", gradient: "from-cyan-500" },
    purple: { bg: "bg-purple-500/10", text: "text-purple-400", gradient: "from-purple-500" },
    pink: { bg: "bg-pink-500/10", text: "text-pink-400", gradient: "from-pink-500" }
  };
</script>

<section id="how-it-works" class="relative py-24 md:py-32 bg-[#0a0a0b]">
  <div class="container relative mx-auto px-4">
    <!-- Section Header -->
    <div class="text-center max-w-3xl mx-auto mb-16">
      <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-400 text-sm font-medium mb-4 border border-cyan-500/20">
        How It Works
      </div>
      <h2 class="text-3xl md:text-5xl font-bold text-white mb-4">
        From Documents to AI Agent
        <span class="bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-indigo-400">
          in Minutes
        </span>
      </h2>
      <p class="text-lg text-gray-400">
        Get your AI assistant up and running with just a few simple steps.
      </p>
    </div>

    <!-- Steps -->
    <div class="relative max-w-4xl mx-auto">
      <!-- Connection Line -->
      <div class="absolute left-8 md:left-1/2 top-0 bottom-0 w-px bg-gradient-to-b from-indigo-500/50 via-cyan-500/50 to-purple-500/50 hidden md:block"></div>

      <div class="space-y-12 md:space-y-0">
        {#each steps as step, index}
          {@const colors = colorClasses[step.color]}
          {@const isEven = index % 2 === 0}

          <div class="relative md:flex md:items-center md:gap-8 {isEven ? '' : 'md:flex-row-reverse'}">
            <!-- Step Number & Icon (Center on desktop) -->
            <div class="absolute left-0 md:left-1/2 md:-translate-x-1/2 flex items-center justify-center">
              <div class="relative">
                <div class="h-16 w-16 rounded-2xl {colors.bg} border border-white/10 flex items-center justify-center backdrop-blur-sm">
                  <step.icon class="h-7 w-7 {colors.text}" />
                </div>
                <!-- Step Number Badge -->
                <div class="absolute -top-2 -right-2 h-6 w-6 rounded-full bg-gradient-to-br {colors.gradient} to-transparent flex items-center justify-center text-xs font-bold text-white">
                  {index + 1}
                </div>
              </div>
            </div>

            <!-- Content Card -->
            <div class="ml-24 md:ml-0 md:w-[calc(50%-4rem)] {isEven ? 'md:text-right md:pr-8' : 'md:pl-8'}">
              <div class="p-6 rounded-2xl border border-white/10 bg-white/[0.02] hover:bg-white/[0.04] transition-all duration-300">
                <span class="text-xs font-mono {colors.text} mb-2 block">Step {step.step}</span>
                <h3 class="text-xl font-semibold text-white mb-2">{step.title}</h3>
                <p class="text-gray-400 text-sm leading-relaxed">{step.description}</p>
              </div>
            </div>

            <!-- Spacer for opposite side -->
            <div class="hidden md:block md:w-[calc(50%-4rem)]"></div>
          </div>

          {#if index < steps.length - 1}
            <div class="h-8 md:h-24"></div>
          {/if}
        {/each}
      </div>
    </div>
  </div>
</section>
