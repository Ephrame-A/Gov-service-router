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
  recommendations: ServiceRecommendation[];
  alternatives: ServiceRecommendation[];
  question?: string;
  conversation_id?: string;
  top_candidates: ServiceRecommendation[];
  query_id: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user_id: string;
  email: string;
  role: string;
  institution_id?: string;
}

export interface Department {
  id: string;
  institution_id: string;
  name: string;
  description?: string;
}

export interface Service {
  id: string;
  department_id: string;
  office_id?: string;
  name: string;
  description: string;
  example_phrasings: string[];
  required_documents: string[];
  typical_duration?: string;
  fees?: string;
  has_embedding: boolean;
}

export interface Institution {
  id: string;
  name: string;
  type: string;
  description?: string;
  is_approved: boolean;
  created_at: string;
}

// --- Citizen API ---

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

// --- Auth API ---

export async function login(
  email: string,
  password: string
): Promise<AuthResponse> {
  const res = await fetch(`${API_URL}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error("Invalid credentials");
  return res.json();
}

// --- Officer API ---

function authHeaders(token: string) {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
}

export async function listDepartments(
  token: string,
  institutionId: string
): Promise<Department[]> {
  const res = await fetch(
    `${API_URL}/api/institutions/${institutionId}/departments`,
    { headers: authHeaders(token) }
  );
  if (!res.ok) throw new Error("Failed to load departments");
  return res.json();
}

export async function listServices(
  token: string,
  institutionId: string
): Promise<Service[]> {
  const res = await fetch(
    `${API_URL}/api/institutions/${institutionId}/services`,
    { headers: authHeaders(token) }
  );
  if (!res.ok) throw new Error("Failed to load services");
  return res.json();
}

export async function createService(
  token: string,
  data: {
    department_id: string;
    name: string;
    description: string;
    example_phrasings: string[];
    required_documents: string[];
  }
): Promise<Service> {
  const res = await fetch(`${API_URL}/api/services`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create service");
  return res.json();
}

export async function refreshServiceEmbedding(
  token: string,
  serviceId: string
): Promise<Service> {
  const res = await fetch(
    `${API_URL}/api/services/${serviceId}/refresh-embedding`,
    { method: "POST", headers: authHeaders(token) }
  );
  if (!res.ok) throw new Error("Failed to refresh embedding");
  return res.json();
}

// --- Admin API ---

export async function listPendingInstitutions(
  token: string
): Promise<Institution[]> {
  const res = await fetch(`${API_URL}/api/admin/pending-institutions`, {
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error("Failed to load pending institutions");
  return res.json();
}

export async function approveInstitution(
  token: string,
  institutionId: string
): Promise<Institution> {
  const res = await fetch(
    `${API_URL}/api/admin/institutions/${institutionId}/approve`,
    { method: "POST", headers: authHeaders(token) }
  );
  if (!res.ok) throw new Error("Failed to approve institution");
  return res.json();
}
