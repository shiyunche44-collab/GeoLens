import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

// Frontend boundaries (docs/architecture.md §8.1):
//   app/ (routes) -> features/* -> lib/
// A feature never imports another feature; lib never imports features or app.
const boundaries = [
  {
    files: ["src/features/**/*.{ts,tsx}"],
    rules: {
      "no-restricted-imports": ["error", {
        patterns: [
          { group: ["@/features/*", "@/features/**"], message: "Features must not import other features. Share via src/lib or compose in src/app." },
          { group: ["@/app/*", "@/app/**"], message: "Features must not import routes." },
        ],
      }],
    },
  },
  {
    files: ["src/lib/**/*.{ts,tsx}"],
    rules: {
      "no-restricted-imports": ["error", {
        patterns: [{ group: ["@/features/*", "@/features/**", "@/app/*", "@/app/**"], message: "lib is the bottom layer." }],
      }],
    },
  },
];

const config = [
  ...nextVitals,
  ...nextTs,
  ...boundaries,
  { ignores: [".next/**", "node_modules/**", "next-env.d.ts", "src/lib/api/schema.d.ts"] },
];

export default config;
