'use client';
import { useEffect, useRef, useState } from 'react';
import { themeStorageKey, validTheme, type Theme } from '../lib/theme.ts';

export default function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>('light');
  const preference = useRef<Theme | null>(null);
  useEffect(() => {
    const media = window.matchMedia('(prefers-color-scheme: dark)');
    let saved: string | null = null;
    try { saved = localStorage.getItem(themeStorageKey); } catch {}
    const explicit = validTheme(saved) ? saved : null;
    preference.current = explicit;
    const apply = (value: Theme) => { document.documentElement.dataset.theme = value; setTheme(value); };
    apply(explicit ?? (media.matches ? 'dark' : 'light'));
    const systemChanged = () => { if (!preference.current) apply(media.matches ? 'dark' : 'light'); };
    const storageChanged = (event: StorageEvent) => {
      if (event.key !== themeStorageKey && event.key !== null) return;
      const value = validTheme(event.newValue) ? event.newValue : null;
      preference.current = value;
      apply(value ?? (media.matches ? 'dark' : 'light'));
    };
    media.addEventListener('change', systemChanged);
    window.addEventListener('storage', storageChanged);
    return () => { media.removeEventListener('change', systemChanged); window.removeEventListener('storage', storageChanged); };
  }, []);
  const toggle = () => {
    const next = theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = next;
    setTheme(next); preference.current = next;
    try { localStorage.setItem(themeStorageKey, next); } catch {}
  };
  return <button type="button" className="theme-toggle" aria-label="Toggle dark mode" aria-pressed={theme === 'dark'} title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'} onClick={toggle}>
    <svg className="sun" aria-hidden="true" width="15" height="15" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"><circle cx="8" cy="8" r="3"/><path d="M8 1.5v1.3M8 13.2v1.3M1.5 8h1.3M13.2 8h1.3M3.4 3.4l.9.9M11.7 11.7l.9.9M3.4 12.6l.9-.9M11.7 4.3l.9-.9"/></svg>
    <svg className="moon" aria-hidden="true" width="15" height="15" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"><path d="M13.5 9.6A5.8 5.8 0 0 1 6.4 2.5a5.8 5.8 0 1 0 7.1 7.1z"/></svg>
  </button>;
}
