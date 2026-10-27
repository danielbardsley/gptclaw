import type { Metadata } from 'next';
export const metadata: Metadata = { title: 'Getting started' };
export default function Guide() {
  return (
    <>
      <p className="eyebrow">THE FIELD GUIDE</p>
      <h1>Make it yours.</h1>
      <p className="intro">
        Start with one useful page. Keep the words clear and the paths easy to
        follow.
      </p>
      <a href="#first-page">Jump to your first page</a>
      <section aria-labelledby="first-page">
        <div>
          <h2 id="first-page">Your first page</h2>
          <p>
            Replace the example content, keep the shared navigation useful, and
            check your links before sharing.
          </p>
          <p>
            When your changes are ready, rebuild your private preview to see the
            exported pages.
          </p>
        </div>
      </section>
    </>
  );
}
