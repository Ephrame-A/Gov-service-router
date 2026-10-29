"use client";

import { useRef, useState } from "react";
import { submitQuery, submitFeedback, type QueryResponse, type ServiceRecommendation } from "@/lib/api";

const examples = [
  "I lost my passport",
  "How do I register a new business?",
  "I need a birth certificate for my child",
  "My shop's tax certificate expired",
];

function ArrowIcon({ diagonal = false }: { diagonal?: boolean }) {
  return diagonal ? (
    <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M5 19 19 5M8 5h11v11" /></svg>
  ) : (
    <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M4 12h15m-6-6 6 6-6 6" /></svg>
  );
}

function RouteMark() {
  return <span className="route-mark" aria-hidden="true"><svg viewBox="0 0 40 40" fill="none"><path d="M10 29V14a6 6 0 0 1 6-6h8a6 6 0 0 1 6 6v8a6 6 0 0 1-6 6h-6" stroke="currentColor" strokeWidth="2.7" strokeLinecap="round" /><circle cx="10" cy="30" r="3.5" fill="currentColor" /><circle cx="17" cy="28" r="3.5" fill="currentColor" /></svg></span>;
}

function Detail({ label, children }: { label: string; children: React.ReactNode }) {
  return <div className="result-detail"><dt>{label}</dt><dd>{children}</dd></div>;
}

function ResultCard({ rec, rank, primary = false }: { rec: ServiceRecommendation; rank?: number; primary?: boolean }) {
  const mapQuery = rec.office
    ? rec.office.lat != null && rec.office.lng != null
      ? `${rec.office.lat},${rec.office.lng}`
      : `${rec.institution}, ${rec.office.address}`
    : null;
  const mapsUrl = mapQuery
    ? `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(mapQuery)}`
    : null;

  return (
    <article className={`result-card ${primary ? "result-card-primary" : ""}`}>
      <div className="result-card-header">
        <div><span className="eyebrow">{primary ? "RECOMMENDED SERVICE" : rank ? `OPTION ${String(rank).padStart(2, "0")}` : "RELATED SERVICE"}</span><h3>{rec.service_name}</h3><p>{rec.institution}</p></div>
        <span className="confidence-pill" title="Estimated match confidence">{Math.round(rec.confidence * 100)}% match</span>
      </div>
      <dl className="result-details">
        <Detail label="Department">{rec.department}</Detail>
        {rec.office?.address && <Detail label="Address"><span>{rec.office.address}</span>{mapsUrl && <a className="map-link" href={mapsUrl} target="_blank" rel="noopener noreferrer" aria-label={`Open ${rec.institution} location in Google Maps (opens in a new tab)`}>View on Google Maps <ArrowIcon diagonal /></a>}</Detail>}
        {rec.office?.working_hours && <Detail label="Office hours">{rec.office.working_hours}</Detail>}
        {rec.office?.contact_phone && <Detail label="Phone"><a href={`tel:${rec.office.contact_phone}`}>{rec.office.contact_phone}</a></Detail>}
        {rec.office?.contact_email && <Detail label="Email"><a href={`mailto:${rec.office.contact_email}`}>{rec.office.contact_email}</a></Detail>}
      </dl>
      {rec.required_documents.length > 0 && <div className="document-list"><h4>Documents to prepare</h4><ul>{rec.required_documents.map((doc, i) => <li key={`${doc}-${i}`}>{doc}</li>)}</ul></div>}
      <div className="match-reason"><strong>Why this matches</strong><p>{rec.explanation}</p></div>
    </article>
  );
}

function normalizeClarificationQuestion(question: string) {
  const lower = question.toLowerCase();
  const hasUuid = /\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b/i.test(question);
  const hasInternalTerms = ["identical service entries", "database", "service ids", "matched multiple services", "could you provide more details"].some((term) => lower.includes(term));
  return hasUuid || hasInternalTerms ? "I found more than one possible service. Could you clarify which one you need?" : question;
}

export default function HomePage() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [feedbackSent, setFeedbackSent] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const chooseExample = (example: string) => {
    setQuery(example);
    setResult(null);
    setError(null);
    setConversationId(undefined);
    textareaRef.current?.focus();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || loading) return;
    const previousResult = result;
    const followUpId = result?.status === "needs_clarification" ? conversationId : undefined;
    setLoading(true);
    setError(null);
    setResult(null);
    setFeedbackSent(false);
    try {
      const response = await submitQuery(query.trim(), followUpId);
      setResult(response);
      setConversationId(response.conversation_id);
    } catch (err) {
      if (previousResult?.status === "needs_clarification") setResult(previousResult);
      setError(err instanceof Error ? err.message : "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (feedback: "correct" | "incorrect") => {
    if (!result || feedbackSent) return;
    try {
      await submitFeedback(result.query_id, feedback);
      setFeedbackSent(true);
    } catch {
      // Feedback should not interrupt the search experience.
    }
  };

  const matched = result?.status === "matched";
  const recommendations = matched
    ? result.recommendations.length > 0 ? result.recommendations : result.recommendation ? [result.recommendation] : []
    : [];

  return (
    <div className="site-shell">
      <header className="site-header">
        <a className="brand" href="/" aria-label="Tequami home"><RouteMark /><span><strong>Tequami</strong><small>ADDIS ABABA</small></span></a>
        <nav aria-label="Main navigation" className="site-nav"><a href="#how-it-works">How it works</a><a className="nav-portal" href="/officer/login">Officer portal <ArrowIcon diagonal /></a></nav>
      </header>

      <main>
        <section className="hero" aria-labelledby="hero-title">
          <div className="hero-copy">
            <p className="hero-eyebrow">PUBLIC SERVICES IN ADDIS ABABA</p>
            <h1 id="hero-title">Need a public service?<br /><em>Start with your situation.</em></h1>
            <p className="hero-lead">Lost a document, registering a business, or sorting out a tax record? Describe the problem. Tequami will show a likely service, the office details, and documents to check before you go.</p>
            <div className="hero-location">Search in English or Amharic</div>
          </div>

          <div className="finder-panel" id="find-a-service">
            <div className="finder-heading"><div><span className="eyebrow">FIND A SERVICE</span><h2>What happened, or what do you need?</h2></div></div>
            <p className="finder-intro">Use your own words. You do not need to know the name of the office.</p>
            <form onSubmit={handleSubmit}>
              <label className="field-label" htmlFor="service-query">Describe your request</label>
              <textarea ref={textareaRef} id="service-query" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="For example, I need to renew my business license..." rows={5} disabled={loading} />
              <button className="submit-button" type="submit" disabled={loading || !query.trim()}><span>{loading ? "Finding the right service…" : "Find my service"}</span><span className="submit-arrow">{loading ? <span className="loading-spinner" /> : <ArrowIcon />}</span></button>
            </form>
            <div className="finder-examples"><span className="examples-label">EXAMPLE REQUESTS</span><div className="example-grid">{examples.map((example) => <button key={example} type="button" onClick={() => chooseExample(example)} disabled={loading}>{example}</button>)}</div></div>
          </div>
        </section>

        {(error || result || loading) && <section className="results-section" aria-live="polite" aria-busy={loading}>
          <div className="section-heading"><span className="eyebrow">YOUR NEXT STEP</span><h2>Here&apos;s where to go</h2></div>
          {loading && <div className="status-card"><span className="loading-spinner dark" /> Looking for the best route for your request…</div>}
          {error && <div className="status-card error-card" role="alert"><strong>We couldn&apos;t complete your search.</strong><p>{error}</p></div>}
          {matched && recommendations.length > 0 && <>
            <p className="results-intro">{recommendations.length === 1 ? "We found a service that may fit your request." : `We found ${recommendations.length} services that may fit your request.`} Check the details before you visit.</p>
            <div className="results-grid">{recommendations.map((rec, i) => <ResultCard key={`${rec.service_name}-${i}`} rec={rec} rank={i + 1} primary={i === 0} />)}</div>
            {result.alternatives.length > 0 && <div className="alternatives"><h3>Other possibilities</h3><div className="results-grid">{result.alternatives.map((rec, i) => <ResultCard key={`${rec.service_name}-${i}`} rec={rec} rank={i + 1} />)}</div></div>}
            <div className="feedback-panel"><div><strong>Was this helpful?</strong><p>Your feedback helps improve future recommendations.</p></div>{feedbackSent ? <span className="feedback-thanks">Thanks for your feedback.</span> : <div className="feedback-actions"><button type="button" onClick={() => handleFeedback("correct")}>Yes, it helped</button><button type="button" onClick={() => handleFeedback("incorrect")}>Not quite</button></div>}</div>
          </>}
          {result?.status === "needs_clarification" && result.question && <div className="status-card clarification-card"><span className="eyebrow">ONE QUICK QUESTION</span><h3>{normalizeClarificationQuestion(result.question)}</h3><p>Add a little more detail so we can point you in the right direction.</p><button type="button" onClick={() => { setQuery(""); textareaRef.current?.focus(); }}>Answer above <ArrowIcon /></button></div>}
          {result?.status === "no_match" && <div className="no-match"><div className="status-card"><span className="eyebrow">LET&apos;S TRY AGAIN</span><h3>We couldn&apos;t find a confident match.</h3><p>Try describing the document you need, what happened, or the kind of service you&apos;re looking for.</p></div>{result.top_candidates.length > 0 && <div className="alternatives"><h3>These may still be relevant</h3><div className="results-grid">{result.top_candidates.map((rec, i) => <ResultCard key={`${rec.service_name}-${i}`} rec={rec} rank={i + 1} />)}</div></div>}</div>}
        </section>}

        <section className="how-section" id="how-it-works" aria-labelledby="how-title">
          <div className="how-header"><div><span className="eyebrow">WHAT THE RESULTS SHOW</span><h2 id="how-title">Useful details<br /><em>before you visit.</em></h2></div><p>Tequami suggests a service from the directory. Confirm the requirements with the office before making the trip.</p></div>
          <div className="steps-grid"><div className="step-card"><span className="step-number">01 / SERVICE</span><h3>The likely service</h3><p>See the service name, institution, department, and why it may fit your request.</p></div><div className="step-card"><span className="step-number">02 / OFFICE</span><h3>Where to go</h3><p>Find the office address, available contact details, and a Google Maps link when location data is available.</p></div><div className="step-card"><span className="step-number">03 / DOCUMENTS</span><h3>What to check</h3><p>Review listed documents and office hours, then verify current requirements before visiting.</p></div></div>
        </section>
      </main>

      <footer className="site-footer"><div className="footer-brand"><RouteMark /><span>Tequami</span></div><p>Public service guidance for Addis Ababa.</p><span>Verify requirements with the relevant office before visiting.</span></footer>
    </div>
  );
}
