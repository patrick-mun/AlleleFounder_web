#!/usr/bin/env node
// Détecte les classes CSS définies mais absentes des gabarits (CSS-16).
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";

const walk = (path) =>
  readdirSync(path).flatMap((name) => {
    if (name.startsWith(".") || name === "node_modules") return [];
    const full = join(path, name);
    return statSync(full).isDirectory() ? walk(full) : [full];
  });
const files = walk(process.argv[2]);
const ignoreIndex = process.argv.indexOf("--ignore");
const ignored = new Set(
  ignoreIndex >= 0 ? process.argv[ignoreIndex + 1].split(",") : [],
);
const html = files
  .filter((file) => file.endsWith(".html"))
  .map((file) => readFileSync(file, "utf8"))
  .join("\n");
let dead = 0;
for (const file of files.filter((item) => item.endsWith(".css"))) {
  const css = readFileSync(file, "utf8").replace(/\/\*[\s\S]*?\*\//g, "");
  for (const match of css.matchAll(/\.([a-z][a-z0-9-]*)/g)) {
    const name = match[1];
    if (
      !ignored.has(name) &&
      !new RegExp(`class="[^"]*\\b${name}\\b`).test(html)
    ) {
      console.log(
        `${file}  CSS-16  classe .${name} définie mais jamais utilisée`,
      );
      dead++;
    }
  }
}
console.log(`\n${dead} classe(s) inutilisée(s).`);
process.exit(dead > 0 ? 1 : 0);
