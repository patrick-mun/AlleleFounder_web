#!/usr/bin/env node
// Contrôles complémentaires des règles HTML-01, 20, 21, 22 et 40.
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";

const collect = (path) => {
  if (statSync(path).isFile()) return [path];
  return readdirSync(path).flatMap((name) => {
    const full = join(path, name);
    if (name.startsWith(".") || name === "node_modules") return [];
    return statSync(full).isDirectory()
      ? collect(full)
      : full.endsWith(".html")
        ? [full]
        : [];
  });
};

let errors = 0;
let warnings = 0;
for (const file of process.argv.slice(2).flatMap(collect)) {
  const source = readFileSync(file, "utf8");
  const report = (level, rule, message) => {
    console.log(`${file}  ${level}  ${rule}  ${message}`);
    level === "erreur" ? errors++ : warnings++;
  };
  if (/<style[\s>]|\sstyle\s*=/i.test(source))
    report("erreur", "HTML-20", "CSS embarqué interdit");
  if (/\son[a-z]+\s*=/i.test(source))
    report("erreur", "HTML-21", "gestionnaire inline interdit");
  if (/<script(?![^>]*\bsrc=)[^>]*>(?!\s*<\/script>)/i.test(source)) {
    report("erreur", "HTML-22", "script inline interdit");
  }
  for (const match of source.matchAll(/<svg\b([^>]*)>/gi)) {
    if (!/aria-hidden="true"|role="img"/i.test(match[1])) {
      report(
        "avertissement",
        "HTML-40",
        "SVG sans choix accessibilité explicite",
      );
    }
  }
}
console.log(`\n${errors} erreur(s), ${warnings} avertissement(s).`);
process.exit(errors > 0 ? 1 : 0);
