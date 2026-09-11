// Astro emits a handful of tiny inline <script> tags (client:visible /
// client:idle hydration triggers, SectionNav's scroll listener) that a
// strict `script-src 'self'` CSP blocks outright. Rather than relax it with
// 'unsafe-inline', hash each inline script actually present in this build's
// output and allow exactly those — computed post-build so it never drifts
// from what Astro actually generated.
import { readFile, writeFile, readdir } from "node:fs/promises";
import { createHash } from "node:crypto";
import { fileURLToPath } from "node:url";
import path from "node:path";

const distDir = fileURLToPath(new URL("../dist/", import.meta.url));

async function findHtmlFiles(dir) {
  const entries = await readdir(dir, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) files.push(...(await findHtmlFiles(full)));
    else if (entry.name.endsWith(".html")) files.push(full);
  }
  return files;
}

const files = await findHtmlFiles(distDir);

for (const file of files) {
  let html = await readFile(file, "utf8");
  if (!html.includes("__INLINE_SCRIPT_HASHES__")) continue;

  const hashes = new Set();
  const scriptTagRe = /<script(\s[^>]*)?>([\s\S]*?)<\/script>/g;
  let match;
  while ((match = scriptTagRe.exec(html))) {
    const attrs = match[1] ?? "";
    const body = match[2];
    if (/\bsrc\s*=/.test(attrs) || body.trim() === "") continue;
    const hash = createHash("sha256").update(body, "utf8").digest("base64");
    hashes.add(`'sha256-${hash}'`);
  }

  html = html.replace("__INLINE_SCRIPT_HASHES__", [...hashes].join(" "));
  await writeFile(file, html, "utf8");
  console.log(`inject-csp: allowed ${hashes.size} inline script hash(es) in ${path.relative(process.cwd(), file)}`);
}
