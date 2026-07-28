"use client";

import { signIn, useSession } from "next-auth/react";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function OfficerLoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const { data: session, status } = useSession();

  useEffect(() => {
    if (status === "authenticated" && session?.user) {
      router.replace("/officer");
    }
  }, [router, session, status]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const result = await signIn("credentials", {
      email,
      password,
      redirect: false,
    });

    setLoading(false);
    if (result?.error) {
      setError("Invalid email or password");
      return;
    }

    if (result?.ok) {
      router.replace("/officer");
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[radial-gradient(circle_at_top,_rgba(14,116,144,0.12),_transparent_55%)] px-4 py-12">
      <div className="w-full max-w-md rounded-[28px] border border-slate-200 bg-white/90 p-8 shadow-xl backdrop-blur">
        <div className="mb-6 text-center">
          <p className="mb-3 inline-flex rounded-full bg-sky-100 px-3 py-1 text-sm font-semibold text-sky-700">
            Officer access
          </p>
          <h1 className="text-2xl font-semibold text-slate-900">Sign in to the dashboard</h1>
          <p className="mt-2 text-sm text-slate-600">Manage your institution&apos;s service listings securely.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="rounded-2xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>
          )}
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-2xl border border-slate-300 bg-slate-50 px-3 py-2.5 outline-none transition focus:border-sky-500 focus:bg-white focus:ring-4 focus:ring-sky-100"
              required
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-2xl border border-slate-300 bg-slate-50 px-3 py-2.5 outline-none transition focus:border-sky-500 focus:bg-white focus:ring-4 focus:ring-sky-100"
              required
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-2xl bg-sky-600 px-4 py-2.5 font-semibold text-white transition hover:bg-sky-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>

        <p className="mt-5 text-center text-sm text-slate-500">
          <a href="/" className="font-medium text-sky-700 transition hover:underline">
            ← Back to citizen app
          </a>
        </p>
      </div>
    </div>
  );
}
