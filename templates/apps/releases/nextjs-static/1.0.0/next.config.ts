import type { NextConfig } from 'next';
import { basePath } from './lib/site.ts';
const config: NextConfig = {
  output: 'export',
  basePath: basePath(),
  trailingSlash: true,
  poweredByHeader: false,
  images: { unoptimized: true },
};
export default config;
