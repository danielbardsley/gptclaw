import type { NextConfig } from 'next';
const slug = process.env.GPTCLAW_PROJECT_ID;
if (!slug || !/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.test(slug)) {
  throw new Error('GPTCLAW_PROJECT_ID must be set by the project runner');
}
const config: NextConfig = {
  basePath: `/projects/${slug}`,
  trailingSlash: true,
  poweredByHeader: false,
  allowedDevOrigins: process.env.GPTCLAW_DEV_ORIGIN ? [process.env.GPTCLAW_DEV_ORIGIN] : [],
};
export default config;
