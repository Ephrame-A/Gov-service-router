"use client";

import { useState } from "react";
import {
  submitQuery,
  submitFeedback,
  type QueryResponse,
  type ServiceRecommendation,
} from "@/lib/api";

function ResultCard({
  rec,
  rank,
}: {
  rec: ServiceRecommendation;
  rank?: number;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white/90 p-5 shadow-sm backdrop-blur">
      {rank !== undefined && (
        <div className="mb-2 text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-400">
          Alternative #{rank}
        </div>
      )}
      <h3 className="text-lg font-semibold text-slate-900">{rec.service_name}</h3>

      <div className="mt-3 space-y-2 text-sm">
        <div className="flex items-start gap-2">
          <span className="min-w-[100px] font-medium text-slate-500">Institution:</span>
          <span className="text-slate-700">{rec.institution}</span>
        </div>
        <div className="flex items-start gap-2">
          <span className="min-w-[100px] font-medium text-slate-500">Department:</span>
          <span className="text-slate-700">{rec.department}</span>
        </div>
        {rec.office && (
          <>
            <div className="flex items-start gap-2">
              <span className="min-w-[100px] font-medium text-slate-500">Address:</span>
              <span className="text-slate-700">{rec.office.address}</span>
            </div>
            {rec.office.working_hours && (
              <div className="flex items-start gap-2">
                <span className="min-w-[100px] font-medium text-slate-500">Hours:</span>
                <span className="text-slate-700">{rec.office.working_hours}</span>
              </div>
            )}
            {rec.office.contact_phone && (
              <div className="flex items-start gap-2">
                <span className="min-w-[100px] font-medium text-slate-500">Phone:</span>
                <span className="text-slate-700">{rec.office.contact_phone}</span>
              </div>
            )}
            {rec.office.contact_email && (
              <div className="flex items-start gap-2">
                <span className="min-w-[100px] font-medium text-slate-500">Email:</span>
                <span className="text-slate-700">{rec.office.contact_email}</span>
              </div>
            )}
          </>
        )}
        {rec.required_documents.length > 0 && (
          <div className="mt-3">
            <span className="font-medium text-slate-600">Required Documents:</span>
            <ul className="mt-1 list-inside list-disc space-y-0.5 text-slate-700">
              {rec.required_documents.map((doc, i) => (
                <li key={i}>{doc}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <div className="mt-4 rounded-xl border border-sky-100 bg-sky-50/70 p-3 text-sm text-sky-800">
        <strong>Why this match:</strong> {rec.explanation}
      </div>

      <div className="mt-2 flex items-center justify-between">
        <span className="text-xs font-medium text-slate-400">
          Confidence: {(rec.confidence * 100).toFixed(0)}%
        </span>
      </div>
    </div>
  );
}

function normalizeClarificationQuestion(question: string) {
  const lower = question.toLowerCase();
  const hasUuid = /\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b/i.test(question);
  const hasInternalTerms =
    lower.includes("identical service entries") ||
    lower.includes("database") ||
    lower.includes("service ids") ||
    lower.includes("matched multiple services") ||
    lower.includes("could you provide more details");

  if (hasUuid || hasInternalTerms) {
    return "I found more than one possible service. Could you clarify which one you need?";
  }

  return question;
}

export default function HomePage() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [feedbackSent, setFeedbackSent] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);
    setFeedbackSent(false);

    try {
      const response = await submitQuery(query, conversationId);
      setResult(response);
      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (feedback: "correct" | "incorrect") => {
    if (!result) return;
    try {
      await submitFeedback(result.query_id, feedback);
      setFeedbackSent(true);
    } catch {
      // feedback is non-critical
    }
  };

  return (
    <div className="mx-auto flex min-h-screen max-w-6xl flex-col px-4 py-8 sm:px-6 lg:px-8">
      <header className="rounded-[28px] border border-slate-200 bg-gradient-to-br from-slate-900 via-slate-800 to-sky-900 p-8 text-white shadow-xl">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-2xl">
            <p className="mb-3 inline-flex rounded-full border border-white/20 bg-white/10 px-3 py-1 text-sm font-medium backdrop-blur">
              Government services, made simple
            </p>
            <h1 className="text-3xl font-semibold sm:text-4xl">
              Find the right public office in seconds
            </h1>
            <p className="mt-3 text-lg text-slate-200">
              Describe your issue in plain language and get a clear recommendation for the institution, department, documents, and contact details you need.
            </p>
          </div>
          <a
            href="/officer/login"
            className="inline-flex items-center justify-center rounded-full border border-white/30 bg-white/10 px-4 py-2 text-sm font-medium text-white transition hover:bg-white/20"
          >
            Officer portal →
          </a>
        </div>
      </header>

      <main className="mt-8 grid gap-8 lg:grid-cols-[1.1fr_0.9fr]">
        <section className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="mb-2 block text-sm font-semibold text-slate-700">
                Tell us what you need help with
              </label>
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g. 'my shop's tax certificate expired' or 'I need a birth certificate for my baby'"
                rows={4}
                className="w-full resize-none rounded-2xl border border-slate-300 bg-slate-50 px-4 py-3 text-base shadow-sm outline-none transition focus:border-sky-500 focus:bg-white focus:ring-4 focus:ring-sky-100"
                disabled={loading}
              />
            </div>
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="w-full rounded-2xl bg-sky-600 px-6 py-3 font-semibold text-white transition hover:bg-sky-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="h-5 w-5 animate-spin" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Finding the right office...
                </span>
              ) : (
                "Find the Right Office"
              )}
            </button>
          </form>

          {error && (
            <div className="mt-6 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
              <strong>Error:</strong> {error}
            </div>
          )}

          {result && (
            <div className="mt-8 space-y-6">
              {result.status === "matched" && (result.recommendation || result.recommendations.length > 0) && (
                <>
                  <div className="flex items-center gap-2 text-green-700">
                    <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span className="font-semibold">
                      {result.recommendations.length > 1 ? `We found ${result.recommendations.length} matches!` : "We found a match!"}
                    </span>
                  </div>

                  {result.recommendations.length > 1 ? (
                    <div className="space-y-4">
                      {result.recommendations.map((rec, i) => (
                        <ResultCard key={i} rec={rec} rank={i + 1} />
                      ))}
                    </div>
                  ) : (
                    result.recommendation && <ResultCard rec={result.recommendation} />
                  )}

                  {result.alternatives.length > 0 && (
                    <div className="space-y-3">
                      <h3 className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-400">
                        Other possibilities
                      </h3>
                      {result.alternatives.map((alt, i) => (
                        <ResultCard key={i} rec={alt} rank={i + 1} />
                      ))}
                    </div>
                  )}

                  {!feedbackSent ? (
                    <div className="flex flex-wrap items-center gap-3 rounded-2xl bg-slate-100 p-4">
                      <span className="text-sm text-slate-600">Was this helpful?</span>
                      <button type="button" onClick={() => handleFeedback("correct")} className="rounded-full bg-emerald-100 px-3 py-1.5 text-sm font-semibold text-emerald-700 transition hover:bg-emerald-200">
                        👍 Yes
                      </button>
                      <button type="button" onClick={() => handleFeedback("incorrect")} className="rounded-full bg-rose-100 px-3 py-1.5 text-sm font-semibold text-rose-700 transition hover:bg-rose-200">
                        👎 No
                      </button>
                    </div>
                  ) : (
                    <div className="rounded-2xl bg-slate-100 p-4 text-sm text-slate-600">Thank you for your feedback!</div>
                  )}
                </>
              )}

              {result.status === "needs_clarification" && result.question && (
                <div className="rounded-2xl border border-amber-200 bg-amber-50 p-5">
                  <div className="mb-2 flex items-center gap-2 text-amber-700">
                    <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                    </svg>
                    <span className="font-semibold">We need a bit more information</span>
                  </div>
                  <p className="text-amber-800">{normalizeClarificationQuestion(result.question)}</p>
                  <p className="mt-3 text-sm text-amber-600">
                    Please provide more details below and submit again — we&apos;ll remember your previous message.
                  </p>
                  <button
                    type="button"
                    onClick={() => {
                      setQuery("");
                      document.querySelector("textarea")?.focus();
                    }}
                    className="mt-3 rounded-full bg-amber-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-amber-700"
                  >
                    Answer below
                  </button>
                </div>
              )}

              {result.status === "no_match" && (
                <div>
                  <div className="mb-4 flex items-center gap-2 text-slate-600">
                    <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                    <span className="font-semibold">No confident match found</span>
                  </div>
                  {result.top_candidates.length > 0 && (
                    <div className="space-y-3">
                      <p className="text-sm text-slate-500">These services might be related:</p>
                      {result.top_candidates.map((candidate, i) => (
                        <ResultCard key={i} rec={candidate} rank={i + 1} />
                      ))}
                    </div>
                  )}
                  <p className="mt-4 text-sm text-slate-500">Try rephrasing your request or providing more details.</p>
                </div>
              )}
            </div>
          )}
        </section>

        <aside className="space-y-4">
          <div className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-900">Popular requests</h2>
            <ul className="mt-4 space-y-2 text-sm text-slate-600">
              <li className="rounded-xl bg-slate-50 px-3 py-2">Tax certificate renewal</li>
              <li className="rounded-xl bg-slate-50 px-3 py-2">Passport or visa help</li>
              <li className="rounded-xl bg-slate-50 px-3 py-2">Business license or registration</li>
              <li className="rounded-xl bg-slate-50 px-3 py-2">Birth or marriage certificate</li>
            </ul>
          </div>
          <div className="rounded-[28px] border border-slate-200 bg-gradient-to-br from-sky-50 to-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-900">Why citizens use it</h2>
            <ul className="mt-4 space-y-3 text-sm text-slate-600">
              <li>• Fast routing to the right government service</li>
              <li>• Clear document guidance before you visit</li>
              <li>• Helpful follow-up questions for ambiguous requests</li>
            </ul>
          </div>
        </aside>
      </main>
    </div>
  );
}