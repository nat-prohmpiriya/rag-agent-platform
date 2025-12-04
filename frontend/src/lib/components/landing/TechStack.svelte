<script lang="ts">
  const technologies = [
    {
      name: "SvelteKit",
      logo: `<svg viewBox="0 0 256 308" class="h-8 w-8"><path fill="#FF3E00" d="M239.682 40.707C211.113-.182 154.69-12.301 113.895 13.69L42.247 59.356a82.198 82.198 0 0 0-37.135 55.056a86.566 86.566 0 0 0 8.536 55.576a82.425 82.425 0 0 0-12.296 30.719a87.596 87.596 0 0 0 14.964 66.244c28.574 40.893 84.997 53.007 125.787 27.016l71.648-45.664a82.182 82.182 0 0 0 37.135-55.057a86.601 86.601 0 0 0-8.53-55.577a82.397 82.397 0 0 0 12.29-30.718a87.573 87.573 0 0 0-14.963-66.244"/><path fill="#fff" d="M106.889 270.841c-23.102 6.007-47.497-3.036-61.103-22.648a52.685 52.685 0 0 1-9.003-39.85a49.978 49.978 0 0 1 1.713-6.693l1.35-4.115l3.671 2.697a92.447 92.447 0 0 0 28.036 14.007l2.663.808l-.245 2.659a16.067 16.067 0 0 0 2.89 10.656a17.143 17.143 0 0 0 18.397 6.828a15.786 15.786 0 0 0 4.403-1.935l71.67-45.672a14.922 14.922 0 0 0 6.734-9.977a15.923 15.923 0 0 0-2.713-12.011a17.156 17.156 0 0 0-18.404-6.832a15.78 15.78 0 0 0-4.396 1.933l-27.35 17.434a52.298 52.298 0 0 1-14.553 6.391c-23.101 6.007-47.497-3.036-61.101-22.649a52.681 52.681 0 0 1-9.004-39.849a49.428 49.428 0 0 1 22.34-33.114l71.664-45.677a52.218 52.218 0 0 1 14.563-6.398c23.101-6.007 47.497 3.036 61.101 22.648a52.685 52.685 0 0 1 9.004 39.85a50.559 50.559 0 0 1-1.713 6.692l-1.35 4.116l-3.67-2.693a92.373 92.373 0 0 0-28.037-14.013l-2.664-.809l.246-2.658a16.099 16.099 0 0 0-2.89-10.656a17.143 17.143 0 0 0-18.398-6.828a15.786 15.786 0 0 0-4.402 1.935l-71.67 45.674a14.898 14.898 0 0 0-6.73 9.975a15.9 15.9 0 0 0 2.709 12.012a17.156 17.156 0 0 0 18.404 6.832a15.841 15.841 0 0 0 4.402-1.935l27.345-17.427a52.147 52.147 0 0 1 14.552-6.397c23.101-6.006 47.497 3.037 61.102 22.65a52.681 52.681 0 0 1 9.003 39.848a49.453 49.453 0 0 1-22.34 33.12l-71.664 45.673a52.218 52.218 0 0 1-14.563 6.398"/></svg>`
    },
    {
      name: "FastAPI",
      logo: `<svg viewBox="0 0 154 154" class="h-8 w-8"><circle cx="77" cy="77" r="77" fill="#009688"/><path fill="#fff" d="M81.375 18.667l-38.75 70H77.5l-3.875 46.666l38.75-70H77.5z"/></svg>`
    },
    {
      name: "PostgreSQL",
      logo: `<img src="/logos/postgresql-logo.png" alt="PostgreSQL" class="h-8 w-8 object-contain" />`,
      isImage: true
    },
    {
      name: "LiteLLM",
      logo: `<span class="text-3xl">🚅</span>`,
      isEmoji: true
    },
    {
      name: "OpenAI",
      logo: `<svg viewBox="0 0 24 24" class="h-8 w-8"><path fill="#10a37f" d="M22.282 9.821a5.985 5.985 0 0 0-.516-4.91 6.046 6.046 0 0 0-6.51-2.9A6.065 6.065 0 0 0 4.981 4.18a5.985 5.985 0 0 0-3.998 2.9 6.046 6.046 0 0 0 .743 7.097 5.98 5.98 0 0 0 .51 4.911 6.051 6.051 0 0 0 6.515 2.9A5.985 5.985 0 0 0 13.26 24a6.056 6.056 0 0 0 5.772-4.206 5.99 5.99 0 0 0 3.997-2.9 6.056 6.056 0 0 0-.747-7.073zM13.26 22.43a4.476 4.476 0 0 1-2.876-1.04l.141-.081 4.779-2.758a.795.795 0 0 0 .392-.681v-6.737l2.02 1.168a.071.071 0 0 1 .038.052v5.583a4.504 4.504 0 0 1-4.494 4.494zM3.6 18.304a4.47 4.47 0 0 1-.535-3.014l.142.085 4.783 2.759a.771.771 0 0 0 .78 0l5.843-3.369v2.332a.08.08 0 0 1-.033.062L9.74 19.95a4.5 4.5 0 0 1-6.14-1.646zM2.34 7.896a4.485 4.485 0 0 1 2.366-1.973V11.6a.766.766 0 0 0 .388.676l5.815 3.355-2.02 1.168a.076.076 0 0 1-.071 0l-4.83-2.786A4.504 4.504 0 0 1 2.34 7.872zm16.597 3.855l-5.833-3.387L15.119 7.2a.076.076 0 0 1 .071 0l4.83 2.791a4.494 4.494 0 0 1-.676 8.105v-5.678a.79.79 0 0 0-.407-.667zm2.01-3.023l-.141-.085-4.774-2.782a.776.776 0 0 0-.785 0L9.409 9.23V6.897a.066.066 0 0 1 .028-.061l4.83-2.787a4.5 4.5 0 0 1 6.68 4.66zm-12.64 4.135l-2.02-1.164a.08.08 0 0 1-.038-.057V6.075a4.5 4.5 0 0 1 7.375-3.453l-.142.08-4.778 2.758a.795.795 0 0 0-.393.681zm1.097-2.365l2.602-1.5 2.607 1.5v2.999l-2.597 1.5-2.607-1.5z"/></svg>`
    },
    {
      name: "Gemini",
      logo: `<img src="/logos/gemini-logo.png" alt="Gemini" class="h-8 w-8 object-contain rounded-lg" />`,
      isImage: true
    },
    {
      name: "Claude",
      logo: `<img src="/logos/claude-logo.png" alt="Claude" class="h-8 w-8 object-contain rounded-lg" />`,
      isImage: true
    },
    {
      name: "pgvector",
      logo: `<svg viewBox="0 0 24 24" class="h-8 w-8"><defs><linearGradient id="pgvector-grad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#336791"/><stop offset="100%" style="stop-color:#6b9dc4"/></linearGradient></defs><path fill="url(#pgvector-grad)" d="M12 2l-8 4.5v9L12 22l8-6.5v-9L12 2z"/><path fill="#fff" d="M12 6l-4 2.25v4.5L12 15l4-2.25v-4.5L12 6z"/><circle fill="#336791" cx="12" cy="10.5" r="2"/></svg>`
    }
  ];
</script>

<section class="relative py-20 bg-[#0a0a0b]">
  <div class="container mx-auto px-4">
    <!-- Section Header -->
    <div class="text-center mb-12">
      <p class="text-gray-500 text-sm uppercase tracking-wider mb-2">Built with Modern Tech Stack</p>
      <h3 class="text-xl text-gray-400">Powered by industry-leading technologies</h3>
    </div>

    <!-- Tech Logos -->
    <div class="flex flex-wrap justify-center items-center gap-8 md:gap-12">
      {#each technologies as tech}
        <div class="group flex flex-col items-center gap-2 opacity-60 hover:opacity-100 transition-all duration-300">
          <div class="transition-transform group-hover:scale-110">
            {@html tech.logo}
          </div>
          <span class="text-xs text-gray-500 group-hover:text-gray-300 transition-colors">{tech.name}</span>
        </div>
      {/each}
    </div>
  </div>
</section>
