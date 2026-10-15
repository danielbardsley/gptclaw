export interface Settings {
  projectId: string;
  basePath: string;
}
export function settings(
  projectId = process.env.GPTCLAW_PROJECT_ID ?? "local-api",
): Settings {
  if (
    !/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.test(projectId) ||
    projectId.length > 48
  ) {
    throw new Error("Invalid GPTCLAW_PROJECT_ID");
  }
  return { projectId, basePath: `/projects/${projectId}` };
}
