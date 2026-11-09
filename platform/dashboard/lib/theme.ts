export type Theme = 'light' | 'dark';
export const themeStorageKey = 'gptclaw-dashboard-theme';
export const validTheme = (value: unknown): value is Theme => value === 'light' || value === 'dark';

// Run before the body paints. Storage may be unavailable without disabling theming.
// Keep this static: no request, user or snapshot data is interpolated into script.
export const themeBootstrap = `(() => {
  let saved;
  try { saved = localStorage.getItem('gptclaw-dashboard-theme'); } catch {}
  const theme = saved === 'dark' || saved === 'light' ? saved
    : window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  document.documentElement.dataset.theme = theme;
})();`;
