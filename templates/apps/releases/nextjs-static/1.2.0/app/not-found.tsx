import Link from 'next/link';
export default function NotFound() {
  return (
    <>
      <h1>Page not found</h1>
      <p>This path does not lead to a page in the guide.</p>
      <Link href="/">Return home</Link>
    </>
  );
}
