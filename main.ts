// Entry point for the news-image-20261120 bounty program.
//
// Runs the poster renderer (draw_poster.py, same directory) and writes
// exactly one image to /output/entry.png. No network, no randomness:
// two runs produce a byte-identical file.
//
// Usage: node main.ts
import { execFileSync } from "node:child_process";
import { mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = "/output";
const outPath = join(outDir, "entry.png");

mkdirSync(outDir, { recursive: true });
execFileSync("python3", [join(here, "draw_poster.py"), "--out", outPath], {
  stdio: "inherit",
});
console.log(`wrote ${outPath}`);
