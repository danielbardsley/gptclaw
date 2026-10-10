import type { ReactNode } from 'react';
import './globals.css';
export const metadata = { title: 'Hello World', description: 'Your new application' };
export default function Layout({ children }: { children: ReactNode }) {
  return <html lang="en"><body>{children}</body></html>;
}
