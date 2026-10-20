"use client";

import { useRef, useState } from "react";
import { submitQuery, submitFeedback, type QueryResponse, type ServiceRecommendation } from "@/lib/api";

const examples = [
  "I need to renew my passport",
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
  return (
    <article className={`result-card ${primary ? "result-card-primary" : ""}`}>
      <div className="result-card-header">
        <div><span className="eyebrow">{primary ? "RECOMMENDED SERVICE" : rank ? `OPTION ${String(rank).padStart(2, "0")}` : "RELATED SERVICE"}</span><h3>{rec.service_name}</h3><p>{rec.institution}</p></div>
        <span className="confidence-pill" title="Estimated match confidence">{Math.round(rec.confidence * 100)}% match</span>
      </div>
      <dl className="result-details">
        <Detail label="Department">{rec.department}</Detail>
        {rec.office?.address && <Detail label="Address">{rec.office.address}</Detail>}
        {rec.office?.working_hours && <Detail label="Office hours">{rec.office.working_hours}</Detail>}
        {rec.office?.contact_phone && <Detail label="Phone"><a href={`tel:${rec.office.contact_phone}`}>{rec.office.contact_phone}</a></Detail>}
        {rec.office?.contact_email && <Detail label="Email"><a href={`mailto:${rec.office.contact_email}`}>{rec.office.contact_email}</a></Detail>}
      </dl>
      {rec.required_documents.length > 0 && <div className="document-list"><h4>Documents to prepare</h4><ul>{rec.required_documents.map((doc, i) => <li key={`${doc}-${i}`}>{doc}</li>)}</ul></div>}
      <div className="match-reason"><span aria-hidden="true">✦</span><p>{rec.explanation}</p></div>
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
        <a className="brand" href="/" aria-label="Service Router home"><RouteMark /><span><strong>service<span className="brand-dot">.</span>router</strong><small>ADDIS ABABA</small></span></a>
        <nav aria-label="Main navigation" className="site-nav"><a href="#how-it-works">How it works</a><a className="nav-portal" href="/officer/login">Officer portal <ArrowIcon diagonal /></a></nav>
      </header>

      <main>
        <section className="hero" aria-labelledby="hero-title">
          <div className="hero-art" aria-hidden="true"><span className="art-ring art-ring-one" /><span className="art-ring art-ring-two" /><span className="art-ring art-ring-three" /><span className="art-node art-node-one" /><span className="art-node art-node-two" /></div>
          <div className="hero-copy">
            <p className="hero-eyebrow"><span className="eyebrow-line" /> YOUR CITY, MADE EASIER</p>
            <h1 id="hero-title">The right office.<br /><em>A clearer way</em><br />forward.</h1>
            <p className="hero-lead">Government services can be hard to navigate. Tell us what you need in your own words, and we&apos;ll help you find where to go and what to bring.</p>
            <div className="hero-location"><span className="location-dot" /> Made for Addis Ababa <span className="hero-separator" /> English &amp; Amharic requests</div>
          </div>

          <div className="finder-panel" id="find-a-service">
            <div className="finder-heading"><span className="finder-icon" aria-hidden="true">↗</span><div><span className="eyebrow">LET&apos;S GET STARTED</span><h2>What do you need help with?</h2></div></div>
            <p className="finder-intro">A sentence or two is enough. You can write in English or Amharic.</p>
            <form onSubmit={handleSubmit}>
              <label className="field-label" htmlFor="service-query">Describe your request</label>
              <textarea ref={textareaRef} id="service-query" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="For example, I need to renew my business license..." rows={5} disabled={loading} />
              <button className="submit-button" type="submit" disabled={loading || !query.trim()}><span>{loading ? "Finding the right service…" : "Find my service"}</span><span className="submit-arrow">{loading ? <span className="loading-spinner" /> : <ArrowIcon />}</span></button>
            </form>
            <div className="finder-examples"><span className="examples-label">NEED AN IDEA? TRY ONE OF THESE</span><div className="example-grid">{examples.map((example) => <button key={example} type="button" onClick={() => chooseExample(example)} disabled={loading}>{example}<span aria-hidden="true">↗</span></button>)}</div></div>
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
          <div className="how-header"><div><span className="eyebrow">SIMPLE BY DESIGN</span><h2 id="how-title">From question to<br /><em>the right direction.</em></h2></div><p>No need to know the name of an office or department. Start with your situation, and we&apos;ll guide you from there.</p></div>
          <div className="steps-grid"><div className="step-card"><span className="step-number">01</span><span className="step-symbol" aria-hidden="true">✎</span><h3>Tell us your situation</h3><p>Describe what you need in everyday language, in English or Amharic.</p></div><div className="step-card"><span className="step-number">02</span><span className="step-symbol" aria-hidden="true">◎</span><h3>Find your service</h3><p>We match your request with a relevant institution and department.</p></div><div className="step-card"><span className="step-number">03</span><span className="step-symbol" aria-hidden="true">↗</span><h3>Go prepared</h3><p>See the office details and documents to check before your visit.</p></div></div>
        </section>
      </main>

      <footer className="site-footer"><div className="footer-brand"><RouteMark /><span>service<span className="brand-dot">.</span>router</span></div><p>Helping Addis Ababa find its way through public services.</p><span>Verify requirements with the relevant office before visiting.</span></footer>
    </div>
  );
}
