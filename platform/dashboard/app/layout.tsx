import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = { title: 'Projects · GptClaw', description: 'Private development project inventory and service status' };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
