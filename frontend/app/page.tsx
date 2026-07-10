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
    <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
      {rank !== undefined && (
        <div className="mb-2 text-xs font-medium text-gray-400 uppercase tracking-wider">
          Alternative #{rank}
        </div>
      )}
      <h3 className="text-lg font-semibold text-primary-700">
        {rec.service_name}
      </h3>

      <div className="mt-3 space-y-2 text-sm">
        <div className="flex items-start gap-2">
          <span className="font-medium text-gray-600 min-w-[100px]">
            Institution:
          </span>
          <span>{rec.institution}</span>
        </div>
        <div className="flex items-start gap-2">
          <span className="font-medium text-gray-600 min-w-[100px]">
            Department:
          </span>
          <span>{rec.department}</span>
        </div>
        {rec.office && (
          <>
            <div className="flex items-start gap-2">
              <span className="font-medium text-gray-600 min-w-[100px]">
                Address:
              </span>
              <span>{rec.office.address}</span>
            </div>
            {rec.office.working_hours && (
              <div className="flex items-start gap-2">
                <span className="font-medium text-gray-600 min-w-[100px]">
                  Hours:
                </span>
                <span>{rec.office.working_hours}</span>
              </div>
            )}
            {rec.office.contact_phone && (
              <div className="flex items-start gap-2">
                <span className="font-medium text-gray-600 min-w-[100px]">
                  Phone:
                </span>
                <span>{rec.office.contact_phone}</span>
              </div>
            )}
          </>
        )}
        {rec.required_documents.length > 0 && (
          <div className="mt-3">
            <span className="font-medium text-gray-600">
              Required Documents:
            </span>
            <ul className="mt-1 list-disc list-inside text-gray-700 space-y-0.5">
              {rec.required_documents.map((doc, i) => (
                <li key={i}>{doc}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <div className="mt-4 rounded-md bg-blue-50 p-3 text-sm text-blue-800">
        <strong>Why this match:</strong> {rec.explanation}
      </div>

      <div className="mt-2 flex items-center justify-between">
        <span className="text-xs text-gray-400">
          Confidence: {(rec.confidence * 100).toFixed(0)}%
        </span>
      </div>
    </div>
  );
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
      // silently fail — feedback is non-critical
    }
  };

  return (
    <div className="mx-auto max-w-2xl px-4 py-12">
      {/* Header */}
      <div className="text-center mb-10">
        <h1 className="text-3xl font-bold text-gray-900">
          🏛️ Government Service Router
        </h1>
        <p className="mt-2 text-gray-600">
          Describe your problem and we'll direct you to the right office
        </p>
      </div>

      {/* Search form */}
      <form onSubmit={handleSubmit} className="relative">
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Describe what you need help with, e.g. 'my shop's tax certificate expired' or 'I need a birth certificate for my baby'"
          rows={3}
          className="w-full rounded-lg border border-gray-300 px-4 py-3 text-base shadow-sm focus:border-primary-500 focus:ring-2 focus:ring-primary-200 focus:outline-none resize-none"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="mt-3 w-full rounded-lg bg-primary-600 px-6 py-3 text-white font-medium hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <svg
                className="animate-spin h-5 w-5"
                viewBox="0 0 24 24"
                fill="none"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                />
              </svg>
              Finding the right office...
            </span>
          ) : (
            "Find the Right Office"
          )}
        </button>
      </form>

      {/* Error */}
      {error && (
        <div className="mt-6 rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="mt-8 space-y-6">
          {/* Matched */}
          {result.status === "matched" && result.recommendation && (
            <>
              <div className="flex items-center gap-2 text-green-700">
                <svg
                  className="h-5 w-5"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
                </svg>
                <span className="font-semibold">We found a match!</span>
              </div>
              <ResultCard rec={result.recommendation} />

              {/* Alternatives */}
              {result.alternatives.length > 0 && (
                <div className="space-y-3">
                  <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider">
                    Other possibilities
                  </h3>
                  {result.alternatives.map((alt, i) => (
                    <ResultCard key={i} rec={alt} rank={i + 1} />
                  ))}
                </div>
              )}

              {/* Feedback */}
              {!feedbackSent ? (
                <div className="flex items-center gap-3 rounded-lg bg-gray-100 p-4">
                  <span className="text-sm text-gray-600">
                    Was this helpful?
                  </span>
                  <button
                    onClick={() => handleFeedback("correct")}
                    className="rounded-md bg-green-100 px-3 py-1.5 text-sm font-medium text-green-700 hover:bg-green-200 transition-colors"
                  >
                    👍 Yes
                  </button>
                  <button
                    onClick={() => handleFeedback("incorrect")}
                    className="rounded-md bg-red-100 px-3 py-1.5 text-sm font-medium text-red-700 hover:bg-red-200 transition-colors"
                  >
                    👎 No
                  </button>
                </div>
              ) : (
                <div className="rounded-lg bg-gray-100 p-4 text-sm text-gray-600">
                  Thank you for your feedback!
                </div>
              )}
            </>
          )}

          {/* Needs clarification */}
          {result.status === "needs_clarification" && result.question && (
            <div className="rounded-lg border border-amber-200 bg-amber-50 p-5">
              <div className="flex items-center gap-2 text-amber-700 mb-2">
                <svg
                  className="h-5 w-5"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z"
                    clipRule="evenodd"
                  />
                </svg>
                <span className="font-semibold">
                  We need a bit more information
                </span>
              </div>
              <p className="text-amber-800">{result.question}</p>
              <p className="mt-3 text-sm text-amber-600">
                Please update your description above with more details and try
                again.
              </p>
            </div>
          )}

          {/* No match */}
          {result.status === "no_match" && (
            <div>
              <div className="flex items-center gap-2 text-gray-600 mb-4">
                <svg
                  className="h-5 w-5"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                    clipRule="evenodd"
                  />
                </svg>
                <span className="font-semibold">
                  No confident match found
                </span>
              </div>
              {result.top_candidates.length > 0 && (
                <div className="space-y-3">
                  <p className="text-sm text-gray-500">
                    These services might be related:
                  </p>
                  {result.top_candidates.map((candidate, i) => (
                    <ResultCard key={i} rec={candidate} rank={i + 1} />
                  ))}
                </div>
              )}
              <p className="mt-4 text-sm text-gray-500">
                Try rephrasing your request or providing more details.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
