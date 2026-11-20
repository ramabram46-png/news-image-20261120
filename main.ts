// Entry program for the news-image-20261120 bounty (Node 22, stdlib only).
//
// The poster is drawn ahead of time by draw_poster.py and shipped in this
// repository as entry.png. This program only copies that file into the
// output directory, so both grading runs produce byte-identical output:
// no network, no randomness, no timestamps anywhere in the path.
//
// It creates the output directory if it is missing and fails loudly if
// the embedded image is absent, rather than writing a partial entry.
// Outside the grader, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import { join } from "node:path";

const source = new URL("./entry.png", import.meta.url);
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const target = join(outDir, "entry.png");

if (!existsSync(source)) {
  throw new Error("entry.png is missing from the repository");
}
if (!existsSync(outDir)) {
  mkdirSync(outDir, { recursive: true });
}

copyFileSync(source, target);
console.log("wrote", target);
