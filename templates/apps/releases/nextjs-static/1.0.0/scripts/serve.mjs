import { createServer } from 'node:http';
import {
  constants,
  closeSync,
  fstatSync,
  lstatSync,
  openSync,
  readFileSync,
} from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { identity, inventory, sourceDigest } from './export.mjs';
export function verifiedExport(root, id, checkSource = true) {
  const out = path.join(root, 'out');
  if (
    lstatSync(out).isSymbolicLink() ||
    lstatSync(path.join(out, '.gptclaw-build.json')).isSymbolicLink()
  )
    throw new Error('Invalid output root');
  const manifest = JSON.parse(
    readFileSync(path.join(out, '.gptclaw-build.json'), 'utf8'),
  );
  const actual = inventory(out);
  delete actual['.gptclaw-build.json'];
  if (
    manifest.schema_version !== 1 ||
    manifest.project_id !== id ||
    !manifest.files['index.html'] ||
    JSON.stringify(actual) !== JSON.stringify(manifest.files) ||
    (checkSource && manifest.source_digest !== sourceDigest(root))
  )
    throw new Error('Incomplete, altered or mismatched static export');
  return { out, manifest };
}
const types = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json',
  '.txt': 'text/plain; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.webp': 'image/webp',
  '.ico': 'image/x-icon',
  '.woff2': 'font/woff2',
};
export function staticServer(root, id, { checkSource = true } = {}) {
  const { out } = verifiedExport(root, id, checkSource);
  const prefix = `/projects/${id}/`;
  return createServer((req, res) => {
    function send(status, body, type = 'text/plain; charset=utf-8') {
      res.writeHead(status, {
        'Content-Type': type,
        'Content-Length': Buffer.byteLength(body),
        'Cache-Control': 'no-store',
        'X-Content-Type-Options': 'nosniff',
      });
      res.end(req.method === 'HEAD' ? undefined : body);
    }
    if (!['GET', 'HEAD'].includes(req.method)) {
      res.setHeader('Allow', 'GET, HEAD');
      return send(405, 'Method not allowed');
    }
    try {
      const raw = req.url.split('?')[0];
      const decoded = decodeURIComponent(raw);
      if (
        decoded.length > 2048 ||
        /[%\\]/.test(decoded) ||
        [...decoded].some(
          (c) => c.charCodeAt(0) < 32 || c.charCodeAt(0) === 127,
        ) ||
        decoded.split('/').some((p) => p.startsWith('.'))
      )
        return send(400, 'Invalid path');
      if (decoded === prefix.slice(0, -1)) {
        res.writeHead(308, { Location: prefix, 'Cache-Control': 'no-store' });
        return res.end();
      }
      if (!decoded.startsWith(prefix)) return send(404, 'Not found');
      if (decoded === prefix + '_gptclaw/ready') {
        try {
          readFileSync(path.join(out, 'index.html'));
          readFileSync(path.join(out, '.gptclaw-build.json'));
          return send(200, 'ready\n');
        } catch {
          return send(503, 'Incomplete export');
        }
      }
      let relative = decoded.slice(prefix.length);
      let file = path.join(out, relative);
      if (!file.startsWith(out + path.sep) && file !== out)
        return send(400, 'Invalid path');
      let status = 200;
      try {
        let current = out;
        for (const part of relative.split('/').filter(Boolean)) {
          current = path.join(current, part);
          if (lstatSync(current).isSymbolicLink())
            return send(404, 'Not found');
        }
        if (lstatSync(file).isDirectory()) {
          if (!decoded.endsWith('/')) {
            res.writeHead(308, {
              Location: decoded + '/',
              'Cache-Control': 'no-store',
            });
            return res.end();
          }
          file = path.join(file, 'index.html');
        }
      } catch {
        file = path.join(out, '404.html');
        status = 404;
      }
      let fd;
      try {
        fd = openSync(
          file,
          constants.O_RDONLY | constants.O_NOFOLLOW | constants.O_NONBLOCK,
        );
        if (!fstatSync(fd).isFile()) return send(404, 'Not found');
        send(
          status,
          readFileSync(fd),
          types[path.extname(file)] || 'application/octet-stream',
        );
      } catch {
        send(404, 'Not found');
      } finally {
        if (fd !== undefined) closeSync(fd);
      }
    } catch {
      send(400, 'Invalid path');
    }
  });
}
if (
  process.argv[1] &&
  import.meta.url === pathToFileURL(process.argv[1]).href
) {
  const server = staticServer(process.cwd(), identity());
  server.listen(3000, '0.0.0.0', () =>
    console.log('Static preview ready on container port 3000'),
  );
}
