import Link from "next/link";

export default function NotFound() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-black text-white p-6">
      <h1 className="text-6xl font-bold mb-4">404</h1>
      <p className="text-zinc-400 mb-8">Page not found</p>
      <Link href="/" className="px-6 py-3 bg-purple-600 rounded-lg hover:bg-purple-700 transition">
        Go Home
      </Link>
    </div>
  );
}
