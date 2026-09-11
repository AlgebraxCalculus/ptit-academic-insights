import { defineConfig } from "astro/config";
import preact from "@astrojs/preact";

export default defineConfig({
  output: "static",
  integrations: [preact()],
  build: {
    inlineStylesheets: "always",
  },
  compressHTML: true,
  // Explicit, not relying on the bundler default: source maps would expose
  // original file paths and structure in a public build. No sourcemap should
  // ever ship (docs/architecture.md §9 privacy stance).
  vite: {
    build: {
      sourcemap: false,
    },
  },
});
