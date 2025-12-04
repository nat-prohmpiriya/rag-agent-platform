<script lang="ts">
  import { Button } from "$lib/components/ui/button";
  import { ArrowRight, Bot, MessageSquare, FileText, Sparkles } from "lucide-svelte";
</script>

<section class="relative overflow-hidden pt-32 pb-32 md:pt-40 md:pb-48 bg-[#0a0a0b]">
  <!-- Background Grid -->
  <div class="absolute inset-0 bg-[linear-gradient(to_right,#1a1a2e_1px,transparent_1px),linear-gradient(to_bottom,#1a1a2e_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_110%)]"></div>

  <!-- Glow Effects -->
  <div class="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[600px] bg-indigo-500/20 blur-[120px] rounded-full pointer-events-none"></div>
  <div class="absolute top-20 right-1/4 w-[400px] h-[400px] bg-cyan-500/10 blur-[100px] rounded-full pointer-events-none"></div>

  <div class="container relative mx-auto px-4 text-center">
    <!-- Badge -->
    <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-500/10 text-indigo-400 text-sm font-medium mb-8 border border-indigo-500/20 animate-fade-in-up">
      <span class="relative flex h-2 w-2">
        <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
        <span class="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
      </span>
      AI-Powered Document Intelligence
    </div>

    <!-- Main Headline with Gradient -->
    <h1 class="text-5xl md:text-7xl lg:text-8xl font-bold tracking-tight mb-6 animate-fade-in-up delay-100">
      <span class="bg-clip-text text-transparent bg-gradient-to-r from-white via-white to-white/60">
        Build AI Agents
      </span>
      <br />
      <span class="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-purple-400 to-cyan-400">
        That Know Your Data
      </span>
    </h1>

    <!-- Subheadline -->
    <p class="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto mb-10 animate-fade-in-up delay-200">
      Create custom AI chatbots powered by your documents.
      Multi-model support, custom tools, and enterprise-grade privacy.
    </p>

    <!-- CTA Buttons -->
    <div class="flex flex-col sm:flex-row items-center justify-center gap-4 animate-fade-in-up delay-300">
      <Button
        size="lg"
        href="/register"
        class="bg-indigo-600 hover:bg-indigo-700 text-white min-w-[180px] h-12 text-lg shadow-lg shadow-indigo-500/25 group"
      >
        Get Started Free
        <ArrowRight class="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
      </Button>
      <Button
        variant="outline"
        size="lg"
        href="#how-it-works"
        class="min-w-[180px] h-12 text-lg border-white/20 text-gray-300 hover:bg-white/5 hover:text-white"
      >
        See How It Works
      </Button>
    </div>

    <!-- Dashboard Preview Mockup -->
    <div class="mt-20 relative mx-auto max-w-5xl animate-fade-in-up delay-500 perspective-1000">
      <div class="relative rounded-xl border border-white/10 bg-[#0d0d0f]/80 backdrop-blur-xl shadow-2xl shadow-indigo-500/10 overflow-hidden transform rotate-x-6 transition-transform duration-700 hover:rotate-x-0">
        <!-- Mockup Header -->
        <div class="h-12 border-b border-white/10 flex items-center px-4 gap-2 bg-white/5">
          <div class="flex gap-2">
            <div class="w-3 h-3 rounded-full bg-red-500/60"></div>
            <div class="w-3 h-3 rounded-full bg-yellow-500/60"></div>
            <div class="w-3 h-3 rounded-full bg-green-500/60"></div>
          </div>
          <div class="ml-4 h-6 w-64 rounded-md bg-white/5 flex items-center px-3">
            <span class="text-xs text-gray-500">app.ragagent.io/dashboard</span>
          </div>
        </div>

        <!-- Mockup Content -->
        <div class="flex h-[400px] md:h-[500px]">
          <!-- Sidebar -->
          <div class="hidden md:flex w-56 border-r border-white/10 p-4 flex-col gap-2 bg-[#0a0a0b]">
            <div class="h-10 w-full rounded-lg bg-indigo-500/20 flex items-center px-3 gap-2 mb-4">
              <Bot class="h-4 w-4 text-indigo-400" />
              <span class="text-xs text-indigo-300">My Agents</span>
            </div>
            {#each ["Documents", "Tools", "Analytics", "Settings"] as item, i}
              <div class="h-9 w-full rounded-lg bg-white/5 flex items-center px-3">
                <span class="text-xs text-gray-500">{item}</span>
              </div>
            {/each}
          </div>

          <!-- Main Chat Area -->
          <div class="flex-1 flex flex-col">
            <!-- Chat Messages -->
            <div class="flex-1 p-6 space-y-4 overflow-hidden">
              <!-- User Message -->
              <div class="flex justify-end">
                <div class="bg-indigo-600/20 border border-indigo-500/30 rounded-2xl rounded-br-md px-4 py-3 max-w-[70%]">
                  <p class="text-sm text-gray-300">What's our vacation policy?</p>
                </div>
              </div>

              <!-- AI Response -->
              <div class="flex gap-3">
                <div class="h-8 w-8 rounded-full bg-gradient-to-br from-indigo-500 to-cyan-500 flex items-center justify-center flex-shrink-0">
                  <Bot class="h-4 w-4 text-white" />
                </div>
                <div class="bg-white/5 border border-white/10 rounded-2xl rounded-bl-md px-4 py-3 max-w-[70%]">
                  <p class="text-sm text-gray-300 mb-2">Based on the HR Policy document, employees receive:</p>
                  <ul class="text-sm text-gray-400 list-disc list-inside space-y-1">
                    <li>20 days paid vacation annually</li>
                    <li>5 sick days per year</li>
                    <li>Carryover up to 5 days</li>
                  </ul>
                  <div class="mt-3 flex items-center gap-2 text-xs text-indigo-400">
                    <FileText class="h-3 w-3" />
                    <span>Source: HR_Policy_2024.pdf</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Chat Input -->
            <div class="p-4 border-t border-white/10">
              <div class="flex items-center gap-2 bg-white/5 rounded-xl px-4 py-3 border border-white/10">
                <input
                  type="text"
                  placeholder="Ask about your documents..."
                  class="flex-1 bg-transparent text-sm text-gray-300 placeholder-gray-500 outline-none"
                  disabled
                />
                <Button size="sm" class="bg-indigo-600 hover:bg-indigo-700 h-8 px-4">
                  Send
                </Button>
              </div>
            </div>
          </div>

          <!-- Right Panel -->
          <div class="hidden lg:flex w-72 border-l border-white/10 p-4 flex-col gap-4 bg-[#0a0a0b]">
            <!-- Usage Stats -->
            <div class="rounded-xl border border-white/10 bg-white/5 p-4">
              <div class="flex items-center justify-between mb-3">
                <span class="text-sm text-gray-400">Usage</span>
                <Sparkles class="h-4 w-4 text-indigo-400" />
              </div>
              <div class="space-y-3">
                <div>
                  <div class="flex justify-between text-xs text-gray-500 mb-1">
                    <span>Queries</span>
                    <span>2,450 / 5,000</span>
                  </div>
                  <div class="h-2 w-full bg-white/5 rounded-full overflow-hidden">
                    <div class="h-full w-[49%] bg-gradient-to-r from-indigo-500 to-cyan-500 rounded-full"></div>
                  </div>
                </div>
                <div>
                  <div class="flex justify-between text-xs text-gray-500 mb-1">
                    <span>Documents</span>
                    <span>18 / 50</span>
                  </div>
                  <div class="h-2 w-full bg-white/5 rounded-full overflow-hidden">
                    <div class="h-full w-[36%] bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full"></div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Recent Documents -->
            <div class="flex-1 rounded-xl border border-white/10 bg-white/5 p-4">
              <span class="text-sm text-gray-400">Recent Documents</span>
              <div class="mt-3 space-y-2">
                {#each ["HR_Policy.pdf", "Benefits.docx", "Onboarding.pdf"] as doc}
                  <div class="flex items-center gap-2 text-xs text-gray-500 py-2 px-2 rounded-lg hover:bg-white/5">
                    <FileText class="h-3 w-3 text-gray-600" />
                    <span>{doc}</span>
                  </div>
                {/each}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Floating Elements -->
      <div class="absolute -right-4 md:-right-12 top-16 md:top-20 p-3 md:p-4 rounded-xl border border-white/10 bg-[#0d0d0f]/90 backdrop-blur-md shadow-xl animate-float hidden sm:block">
        <div class="flex items-center gap-3">
          <div class="h-10 w-10 rounded-full bg-green-500/20 flex items-center justify-center">
            <FileText class="h-5 w-5 text-green-400" />
          </div>
          <div>
            <div class="text-sm font-medium text-white">Contract.pdf</div>
            <div class="text-xs text-green-400">Indexed</div>
          </div>
        </div>
      </div>

      <div class="absolute -left-4 md:-left-8 bottom-24 md:bottom-32 p-3 md:p-4 rounded-xl border border-white/10 bg-[#0d0d0f]/90 backdrop-blur-md shadow-xl animate-float delay-700 hidden sm:block">
        <div class="flex items-center gap-3">
          <div class="h-10 w-10 rounded-full bg-indigo-500/20 flex items-center justify-center">
            <MessageSquare class="h-5 w-5 text-indigo-400" />
          </div>
          <div>
            <div class="text-sm font-medium text-white">HR Agent</div>
            <div class="text-xs text-indigo-400">Active</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<style>
  .perspective-1000 {
    perspective: 1000px;
  }

  .rotate-x-6 {
    transform: rotateX(6deg);
  }

  :global(.rotate-x-0) {
    transform: rotateX(0deg);
  }

  @keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
  }

  .animate-float {
    animation: float 6s ease-in-out infinite;
  }

  .animate-fade-in-up {
    animation: fadeInUp 0.8s ease-out forwards;
    opacity: 0;
    transform: translateY(20px);
  }

  @keyframes fadeInUp {
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .delay-100 { animation-delay: 100ms; }
  .delay-200 { animation-delay: 200ms; }
  .delay-300 { animation-delay: 300ms; }
  .delay-500 { animation-delay: 500ms; }
  .delay-700 { animation-delay: 700ms; }
</style>
