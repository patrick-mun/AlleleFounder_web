#!/usr/bin/env node
// Contrôle complémentaire de neutralisation du mouvement (CSS-41).
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";

const collect = (path) => {
  if (statSync(path).isFile()) return [path];
  return readdirSync(path).flatMap((name) => {
    const full = join(path, name);
    if (name.startsWith(".") || name === "node_modules") return [];
    return statSync(full).isDirectory()
      ? collect(full)
      : full.endsWith(".css")
        ? [full]
        : [];
  });
};

let warnings = 0;
for (const file of process.argv.slice(2).flatMap(collect)) {
  const source = readFileSync(file, "utf8");
  if (
    /\b(?:animation|transition)\s*:/.test(source) &&
    !/prefers-reduced-motion/.test(source)
  ) {
    console.log(
      `${file}  avertissement  CSS-41  mouvement sans neutralisation`,
    );
    warnings++;
  }
}
console.log(`\n0 erreur(s), ${warnings} avertissement(s).`);
