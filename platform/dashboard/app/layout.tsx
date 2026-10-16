import type { Metadata } from 'next';
import './globals.css';
import { themeBootstrap } from '../lib/theme.ts';
export const metadata: Metadata = { title: 'Projects · GptClaw', description: 'Private development project inventory and service status' };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en" suppressHydrationWarning><head><script dangerouslySetInnerHTML={{ __html: themeBootstrap }}/></head><body>{children}</body></html>;
}
