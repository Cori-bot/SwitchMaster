import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from "path";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  base: "./",
  root: path.join(__dirname),
  build: {
    outDir: "dist",
    emptyOutDir: true,
    rollupOptions: {
      output: {
        manualChunks(id) {
          const norm = id.replace(/\\/g, "/");
          if (norm.includes("node_modules")) {
            if (
              norm.includes("/react-dom/") ||
              norm.includes("/react/") ||
              norm.includes("/scheduler/")
            ) {
              return "vendor-react";
            }
            if (
              norm.includes("/framer-motion/") ||
              norm.includes("/motion/") ||
              norm.includes("/motion-dom/") ||
              norm.includes("/motion-utils/")
            ) {
              return "vendor-motion";
            }
            return "vendor";
          }
          if (norm.includes("/designs/classic/")) return "design-classic";
        },
      },
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src/renderer"),
      "@assets": path.resolve(__dirname, "./src/assets"),
    },
  },
  server: {
    port: 3000,
    strictPort: true,
  },
});
