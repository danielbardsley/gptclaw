import type { Metadata } from 'next';
import Link from 'next/link';
import { basePath } from '../lib/site';
import './globals.css';
export const metadata: Metadata = {
  title: { default: 'Field guide', template: '%s | Field guide' },
  description: 'A small, accessible static website you can make your own.',
};
export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" href={`${basePath()}/mark.svg`} type="image/svg+xml" />
      </head>
      <body>
        <a className="skip" href="#main">
          Skip to content
        </a>
        <header>
          <Link href="/" className="brand">
            Field guide
          </Link>
          <nav aria-label="Main navigation">
            <Link href="/">Home</Link>
            <Link href="/guide/getting-started/">Getting started</Link>
          </nav>
        </header>
        <main id="main" tabIndex={-1}>
          {children}
        </main>
        <footer>A little space for your next idea.</footer>
      </body>
    </html>
  );
}
