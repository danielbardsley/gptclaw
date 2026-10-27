export function basePath(): string {
  const slug = process.env.GPTCLAW_PROJECT_ID;
  if (
    !slug ||
    !/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.test(slug) ||
    slug.length > 48
  ) {
    throw new Error('A valid GPTCLAW_PROJECT_ID is required');
  }
  return `/projects/${slug}`;
}
