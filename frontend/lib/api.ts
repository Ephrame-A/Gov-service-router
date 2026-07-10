/**
 * Typed API client for the Government Service Router backend.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// --- Types ---

export interface OfficeInfo {
  address: string;
  working_hours?: string;
  contact_phone?: string;
  contact_email?: string;
}

export interface ServiceRecommendation {
  institution: string;
  department: string;
  office?: OfficeInfo;
  service_name: string;
  required_documents: string[];
  confidence: number;
  explanation: string;
}

export type QueryStatus = "matched" | "needs_clarification" | "no_match";

export interface QueryResponse {
  status: QueryStatus;
  recommendation?: ServiceRecommendation;
  alternatives: ServiceRecommendation[];
  question?: string;
  conversation_id?: string;
  top_candidates: ServiceRecommendation[];
  query_id: string;
}

// --- API calls ---

export async function submitQuery(
  text: string,
  conversationId?: string
): Promise<QueryResponse> {
  const res = await fetch(`${API_URL}/api/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, conversation_id: conversationId }),
  });

  if (!res.ok) {
    const error = await res.text();
    throw new Error(`Query failed: ${res.status} — ${error}`);
  }

  return res.json();
}

export async function submitFeedback(
  queryId: string,
  feedback: "correct" | "incorrect"
): Promise<void> {
  const res = await fetch(`${API_URL}/api/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query_id: queryId, feedback }),
  });

  if (!res.ok) {
    const error = await res.text();
    throw new Error(`Feedback failed: ${res.status} — ${error}`);
  }
}
