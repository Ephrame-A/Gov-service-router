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
    if (status === "authenticated" && session?.user) router.replace("/officer");
  }, [router, session, status]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const result = await signIn("credentials", { email, password, redirect: false });
      if (result?.error || !result?.ok) {
        setError("Invalid email or password. Please try again.");
      } else {
        router.replace("/officer");
      }
    } catch {
      setError("Unable to sign in right now. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="login-layout">
      <section className="login-story"><a className="login-brand" href="/"><span className="staff-brand-symbol" aria-hidden="true">↗</span><span>service<span className="brand-dot">.</span>router</span></a><div><span className="login-eyebrow">OFFICER WORKSPACE</span><h1>Better service<br /><em>starts here.</em></h1><p>Keep your institution&apos;s services clear, current, and easy for people to find.</p></div><span className="login-location">ADDIS ABABA · ETHIOPIA</span></section>
      <section className="login-form-side"><div className="login-card"><span className="eyebrow">WELCOME BACK</span><h2>Sign in to your workspace</h2><p>Use your officer or administrator account to continue.</p>
        <form onSubmit={handleSubmit} className="login-form">
          {error && <div className="staff-error" role="alert">{error}</div>}
          <label htmlFor="officer-email">Email address</label><input id="officer-email" type="email" autoComplete="username" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@institution.gov.et" required />
          <label htmlFor="officer-password">Password</label><input id="officer-password" type="password" autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Enter your password" required />
          <button type="submit" disabled={loading}>{loading ? "Signing in…" : "Sign in"}<span aria-hidden="true">→</span></button>
        </form>
        <a className="login-back" href="/">← Back to citizen portal</a>
      </div></section>
    </main>
  );
}
