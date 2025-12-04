<script lang="ts">
  import { Button } from "$lib/components/ui/button";
  import { ArrowRight, Sparkles } from "lucide-svelte";
</script>

<section class="relative py-24 md:py-32 bg-[#0a0a0b] overflow-hidden">
  <!-- Background Glow -->
  <div class="absolute inset-0 bg-gradient-to-t from-indigo-500/10 via-transparent to-transparent"></div>
  <div class="absolute bottom-0 left-1/2 -translate-x-1/2 w-[600px] h-[400px] bg-indigo-500/20 blur-[120px] rounded-full pointer-events-none"></div>

  <div class="container relative mx-auto px-4">
    <div class="max-w-3xl mx-auto text-center">
      <!-- Badge -->
      <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-500/10 text-indigo-400 text-sm font-medium mb-8 border border-indigo-500/20">
        <Sparkles class="h-4 w-4" />
        Start Building Today
      </div>

      <!-- Headline -->
      <h2 class="text-3xl md:text-5xl lg:text-6xl font-bold text-white mb-6">
        Ready to Build Your
        <span class="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-purple-400 to-cyan-400">
          AI Agent?
        </span>
      </h2>

      <!-- Description -->
      <p class="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto mb-10">
        Join thousands of developers and businesses building intelligent AI assistants.
        Get started free, no credit card required.
      </p>

      <!-- CTA Buttons -->
      <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
        <Button
          size="lg"
          href="/register"
          class="bg-indigo-600 hover:bg-indigo-700 text-white min-w-[200px] h-14 text-lg shadow-lg shadow-indigo-500/25 group"
        >
          Get Started Free
          <ArrowRight class="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
        </Button>
        <Button
          variant="outline"
          size="lg"
          href="/login"
          class="min-w-[200px] h-14 text-lg border-white/20 text-gray-300 hover:bg-white/5 hover:text-white"
        >
          Sign In
        </Button>
      </div>

      <!-- Trust Indicators -->
      <div class="mt-12 flex flex-wrap items-center justify-center gap-8 text-sm text-gray-500">
        <div class="flex items-center gap-2">
          <svg class="h-4 w-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
          </svg>
          Free forever plan
        </div>
        <div class="flex items-center gap-2">
          <svg class="h-4 w-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
          </svg>
          No credit card required
        </div>
        <div class="flex items-center gap-2">
          <svg class="h-4 w-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
          </svg>
          Setup in minutes
        </div>
      </div>
    </div>
  </div>
</section>
