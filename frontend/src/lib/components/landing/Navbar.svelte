<script lang="ts">
  import { Button } from "$lib/components/ui/button";
  import { Menu, X } from "lucide-svelte";

  let mobileMenuOpen = $state(false);

  const navLinks = [
    { href: "#features", label: "Features" },
    { href: "#how-it-works", label: "How It Works" },
    { href: "#pricing", label: "Pricing" },
    { href: "#faq", label: "FAQ" },
  ];
</script>

<nav class="fixed top-0 left-0 right-0 z-50 border-b border-white/10 bg-[#0a0a0b]/80 backdrop-blur-xl">
  <div class="container mx-auto px-4">
    <div class="flex h-16 items-center justify-between">
      <!-- Logo -->
      <a href="/" class="flex items-center gap-2">
        <div class="h-8 w-8 rounded-lg bg-gradient-to-br from-indigo-500 to-cyan-500 flex items-center justify-center">
          <svg class="h-5 w-5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
          </svg>
        </div>
        <span class="font-semibold text-lg text-white">RAG Agent</span>
      </a>

      <!-- Desktop Nav Links -->
      <div class="hidden md:flex items-center gap-8">
        {#each navLinks as link}
          <a
            href={link.href}
            class="text-sm text-gray-400 hover:text-white transition-colors"
          >
            {link.label}
          </a>
        {/each}
      </div>

      <!-- Desktop Auth Buttons -->
      <div class="hidden md:flex items-center gap-3">
        <Button variant="ghost" href="/login" class="text-gray-300 hover:text-white hover:bg-white/5">
          Login
        </Button>
        <Button href="/register" class="bg-indigo-600 hover:bg-indigo-700 text-white">
          Get Started
        </Button>
      </div>

      <!-- Mobile Menu Button -->
      <button
        class="md:hidden p-2 text-gray-400 hover:text-white"
        onclick={() => mobileMenuOpen = !mobileMenuOpen}
      >
        {#if mobileMenuOpen}
          <X class="h-6 w-6" />
        {:else}
          <Menu class="h-6 w-6" />
        {/if}
      </button>
    </div>

    <!-- Mobile Menu -->
    {#if mobileMenuOpen}
      <div class="md:hidden py-4 border-t border-white/10">
        <div class="flex flex-col gap-4">
          {#each navLinks as link}
            <a
              href={link.href}
              class="text-sm text-gray-400 hover:text-white transition-colors py-2"
              onclick={() => mobileMenuOpen = false}
            >
              {link.label}
            </a>
          {/each}
          <div class="flex flex-col gap-2 pt-4 border-t border-white/10">
            <Button variant="ghost" href="/login" class="justify-start text-gray-300">
              Login
            </Button>
            <Button href="/register" class="bg-indigo-600 hover:bg-indigo-700 text-white">
              Get Started
            </Button>
          </div>
        </div>
      </div>
    {/if}
  </div>
</nav>
