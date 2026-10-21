import { readFileSync, lstatSync } from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { gzipSync } from 'node:zlib';
import { parse } from 'parse5';
import { inventory, identity } from './export.mjs';
export function checkOutput(out, id) {
  const files = Object.keys(inventory(out)).filter(
    (f) => f !== '.gptclaw-build.json',
  );
  const prefix = `/projects/${id}/`;
  const origin = 'http://static.invalid';
  const external = new Set();
  const pages = new Map();
  function disk(url) {
    const name = decodeURIComponent(url.pathname);
    if (
      !name.startsWith(prefix) ||
      name.split('/').some((s) => s.startsWith('.'))
    )
      throw new Error('Reference escapes private prefix: ' + name);
    let rel = name.slice(prefix.length);
    if (!rel || rel.endsWith('/')) rel += 'index.html';
    else if (!files.includes(rel) && files.includes(rel + '/index.html'))
      rel += '/index.html';
    if (!files.includes(rel)) throw new Error('Broken reference: ' + name);
    return rel;
  }
  function nodes(node, visit) {
    visit(node);
    for (const child of node.childNodes || []) nodes(child, visit);
    if (node.content) nodes(node.content, visit);
  }
  for (const file of files.filter((f) => f.endsWith('.html'))) {
    const refs = [];
    const ids = new Set();
    nodes(parse(readFileSync(path.join(out, file), 'utf8')), (node) => {
      const attrs = Object.fromEntries(
        (node.attrs || []).map(({ name, value }) => [name, value]),
      );
      if (attrs.id) ids.add(attrs.id);
      for (const attr of ['href', 'src', 'poster']) {
        if (attrs[attr])
          refs.push({
            value: attrs[attr],
            asset: !(node.tagName === 'a' && attr === 'href'),
          });
      }
      if (attrs.srcset)
        for (const value of attrs.srcset.split(','))
          refs.push({ value: value.trim().split(/\s+/)[0], asset: true });
      if (attrs.style)
        for (const match of attrs.style.matchAll(
          /url\(\s*['"]?([^'"\s)]+)['"]?\s*\)/g,
        ))
          refs.push({ value: match[1], asset: true });
    });
    pages.set(file, { refs, ids });
  }
  const total = files.reduce(
    (sum, file) => sum + lstatSync(path.join(out, file)).size,
    0,
  );
  if (total > 10 * 1024 * 1024) throw new Error('Whole export exceeds 10 MiB');
  const report = [];
  for (const [file, page] of pages) {
    const pagePath =
      file === 'index.html'
        ? ''
        : file.endsWith('/index.html')
          ? file.slice(0, -10)
          : file;
    const base = new URL(prefix + pagePath, origin);
    const assets = new Set();
    function resolve(value, asset) {
      if (/^(data:|mailto:|tel:)/i.test(value)) return;
      const url = new URL(value, base);
      if (url.origin !== origin) {
        external.add(url.href);
        if (asset) throw new Error('Remote runtime asset: ' + url.href);
        return;
      }
      const target = disk(url);
      if (
        url.hash &&
        pages.has(target) &&
        !pages.get(target).ids.has(decodeURIComponent(url.hash.slice(1)))
      )
        throw new Error('Broken fragment: ' + url.href);
      if (!asset || assets.has(target)) return;
      assets.add(target);
      if (target.endsWith('.css')) {
        const css = readFileSync(path.join(out, target), 'utf8');
        for (const match of css.matchAll(
          /(?:url\(\s*['"]?([^'"\s)]+)['"]?\s*\)|@import\s+['"]([^'"]+)['"])/g,
        )) {
          const resolved = new URL(
            match[1] || match[2],
            new URL(prefix + target, origin),
          );
          resolve(resolved.href, true);
        }
      }
    }
    for (const ref of page.refs) resolve(ref.value, ref.asset);
    const sizes = {
      html: lstatSync(path.join(out, file)).size,
      js: 0,
      css: 0,
      media: 0,
    };
    for (const asset of assets) {
      const bytes = readFileSync(path.join(out, asset));
      if (/\.m?js$/.test(asset)) sizes.js += gzipSync(bytes).length;
      else if (asset.endsWith('.css')) sizes.css += gzipSync(bytes).length;
      else sizes.media += bytes.length;
    }
    if (
      sizes.html > 100 * 1024 ||
      sizes.js > 300 * 1024 ||
      sizes.css > 50 * 1024 ||
      sizes.media > 1024 * 1024
    )
      throw new Error(
        'Page asset budget exceeded: ' + file + ' ' + JSON.stringify(sizes),
      );
    report.push({ page: file, bytes: sizes, unique_assets: assets.size });
  }
  return {
    total_bytes: total,
    pages: report,
    external_references: [...external].sort(),
  };
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href)
  console.log(
    JSON.stringify(
      checkOutput(path.join(process.cwd(), 'out'), identity()),
      null,
      2,
    ),
  );
