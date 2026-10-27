import Link from 'next/link';
import { basePath } from '../lib/site';
export default function Home() {
  return (
    <>
      <p className="eyebrow">YOUR OWN CORNER OF THE WEB</p>
      <h1>
        A small beginning.
        <br />
        Room to grow.
      </h1>
      <p className="intro">
        A clear place for useful ideas. Edit these pages, add your own words,
        and build something worth sharing.
      </p>
      <Link className="button" href="/guide/getting-started/">
        Explore the guide
      </Link>
      <section aria-labelledby="built-for">
        <img
          src={`${basePath()}/mark.svg`}
          alt="A green leaf within a circle"
          width="96"
          height="96"
        />
        <div>
          <h2 id="built-for">Light by design</h2>
          <p>
            Real pages, local assets, and a simple foundation. Your content is
            ready even when JavaScript is off.
          </p>
        </div>
      </section>
    </>
  );
}
