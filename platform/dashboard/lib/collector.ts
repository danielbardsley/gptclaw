import http from 'node:http';
export function readCollector(): Promise<unknown> {
  return new Promise((resolve, reject) => {
    const request = http.request({ socketPath: process.env.DASHBOARD_SOCKET || '/run/gptclaw/collector.sock', path: '/v1/snapshot', method: 'GET', timeout: 2500 }, (response) => {
      const chunks: Buffer[] = [];
      let size = 0;
      response.on('data', (chunk: Buffer) => {
        size += chunk.length;
        if (size > 1024 * 1024) { response.destroy(); reject(new Error('collector-unavailable')); }
        else chunks.push(chunk);
      });
      response.on('error', () => reject(new Error('collector-unavailable')));
      response.on('end', () => {
        try {
          if (response.statusCode !== 200) throw new Error('collector-unavailable');
          resolve(JSON.parse(Buffer.concat(chunks).toString('utf8')));
        } catch { reject(new Error('collector-unavailable')); }
      });
    });
    request.on('timeout', () => request.destroy());
    request.on('error', () => reject(new Error('collector-unavailable')));
    request.end();
  });
}
