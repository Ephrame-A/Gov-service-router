"use client";

import { useSession } from "next-auth/react";
import { useEffect, useState } from "react";
import StaffShell from "@/components/StaffShell";
import {
  approveInstitution, createInstitution, createOfficer, listInstitutions,
  listOfficers, listPendingInstitutions, type Institution, type Officer,
} from "@/lib/api";

type InstitutionType = "federal" | "regional" | "municipal";

export default function AdminDashboard() {
  const { data: session } = useSession();
  const token = session?.accessToken;
  const [pending, setPending] = useState<Institution[]>([]);
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [officers, setOfficers] = useState<Officer[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [approvingId, setApprovingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [institutionId, setInstitutionId] = useState("");
  const [newInstitution, setNewInstitution] = useState<{ name: string; type: InstitutionType; description: string }>({ name: "", type: "federal", description: "" });

  useEffect(() => {
    if (!token) return;
    Promise.all([listPendingInstitutions(token), listInstitutions(token), listOfficers(token)])
      .then(([requests, directory, accounts]) => {
        setPending(requests);
        setInstitutions(directory);
        setOfficers(accounts);
      })
      .catch(() => setError("Admin records could not be loaded. Refresh the page to try again."))
      .finally(() => setLoading(false));
  }, [token]);

  const approved = institutions.filter((institution) => institution.is_approved);

  const handleApprove = async (id: string) => {
    if (!token || approvingId) return;
    setApprovingId(id);
    setError(null);
    setNotice(null);
    try {
      const institution = await approveInstitution(token, id);
      setPending((current) => current.filter((item) => item.id !== id));
      setInstitutions((current) => current.map((item) => item.id === id ? institution : item));
      setNotice(`${institution.name} is approved. You can now add its officers.`);
    } catch {
      setError("The institution could not be approved.");
    } finally {
      setApprovingId(null);
    }
  };

  const handleCreateOfficer = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!token || saving || !institutionId) return;
    setSaving(true);
    setError(null);
    setNotice(null);
    try {
      const officer = await createOfficer(token, { email: email.trim().toLowerCase(), password, institution_id: institutionId });
      setOfficers((current) => [...current, officer].sort((a, b) => a.email.localeCompare(b.email)));
      setEmail("");
      setPassword("");
      setNotice(`${officer.email} can sign in. Share the temporary password through a private channel.`);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "The officer account could not be created.");
    } finally {
      setSaving(false);
    }
  };

  const handleCreateInstitution = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!token || saving) return;
    setSaving(true);
    setError(null);
    setNotice(null);
    try {
      const institution = await createInstitution(token, {
        name: newInstitution.name.trim(), type: newInstitution.type, description: newInstitution.description.trim(),
      });
      setInstitutions((current) => [...current, institution]);
      setInstitutionId(institution.id);
      setNewInstitution({ name: "", type: "federal", description: "" });
      setNotice(`${institution.name} was added to the approved directory.`);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "The institution could not be added.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <StaffShell role="Admin" title="Officer accounts" subtitle="Verify requests through official channels, then add approved officers to their institution." email={session?.user?.email}>
      {error && <div className="staff-error" role="alert">{error}</div>}
      {notice && <div className="staff-success" role="status">{notice}</div>}
      <div className="admin-workflow">
        <section className="staff-section" aria-labelledby="create-officer-title">
          <div className="staff-section-heading"><div><span className="eyebrow">AFTER VERIFICATION</span><h2 id="create-officer-title">Add an officer</h2></div></div>
          <form className="staff-form" onSubmit={handleCreateOfficer}>
            <p className="staff-inline-note">Confirm the person works for the institution before creating an account. Only approved institutions appear here.</p>
            <div className="staff-form-grid">
              <label>Officer email<input type="email" autoComplete="off" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="name@institution.gov.et" required /></label>
              <label>Institution<select value={institutionId} onChange={(event) => setInstitutionId(event.target.value)} required><option value="">Select an institution</option>{approved.map((institution) => <option key={institution.id} value={institution.id}>{institution.name}</option>)}</select></label>
            </div>
            <label>Temporary password<input type="password" autoComplete="new-password" minLength={12} value={password} onChange={(event) => setPassword(event.target.value)} required /></label>
            <p className="staff-inline-note">Use at least 12 characters. Give the password to the officer privately and ask them to change it after signing in.</p>
            <button className="staff-primary-button" type="submit" disabled={saving || loading || approved.length === 0}>{saving ? "Creating account…" : "Create officer account"}</button>
          </form>
        </section>

        <section className="staff-section" aria-labelledby="officers-title">
          <div className="staff-section-heading"><div><span className="eyebrow">ACTIVE ACCOUNTS</span><h2 id="officers-title">Registered officers</h2></div><span className="staff-count">{officers.length}</span></div>
          {loading ? <div className="staff-empty"><p>Loading accounts…</p></div> : officers.length === 0 ? <div className="staff-empty"><p>No officers have been added yet.</p></div> : <div className="staff-service-list">{officers.map((officer) => <article key={officer.id} className="staff-service-card"><div><h3>{officer.email}</h3><p>{officer.institution_name}</p></div></article>)}</div>}
        </section>

        <section className="staff-section" aria-labelledby="pending-title">
          <div className="staff-section-heading"><div><span className="eyebrow">INSTITUTIONS</span><h2 id="pending-title">Pending approval</h2></div><span className="staff-count">{pending.length} pending</span></div>
          {loading ? <div className="staff-empty"><p>Loading institutions…</p></div> : pending.length === 0 ? <div className="staff-empty"><p>No institutions are waiting for approval.</p></div> : <div className="staff-service-list">{pending.map((institution) => <article key={institution.id} className="staff-service-card staff-approval-card"><div><h3>{institution.name}</h3><p>{institution.type}{institution.description ? ` · ${institution.description}` : ""}</p></div><button type="button" className="staff-primary-button" disabled={approvingId === institution.id} onClick={() => handleApprove(institution.id)}>{approvingId === institution.id ? "Approving…" : "Approve institution"}</button></article>)}</div>}
        </section>

        <section className="staff-section" aria-labelledby="new-institution-title">
          <div className="staff-section-heading"><div><span className="eyebrow">AFTER VERIFICATION</span><h2 id="new-institution-title">Add an institution</h2></div></div>
          <form className="staff-form" onSubmit={handleCreateInstitution}>
            <p className="staff-inline-note">Use this when a verified institution is missing from the directory. Institutions added here are approved immediately.</p>
            <div className="staff-form-grid">
              <label>Institution name<input value={newInstitution.name} onChange={(event) => setNewInstitution({ ...newInstitution, name: event.target.value })} required /></label>
              <label>Type<select value={newInstitution.type} onChange={(event) => setNewInstitution({ ...newInstitution, type: event.target.value as InstitutionType })}><option value="federal">Federal</option><option value="regional">Regional</option><option value="municipal">Municipal</option></select></label>
            </div>
            <label>Description<textarea value={newInstitution.description} onChange={(event) => setNewInstitution({ ...newInstitution, description: event.target.value })} rows={2} /></label>
            <button className="staff-primary-button" type="submit" disabled={saving || loading}>{saving ? "Adding institution…" : "Add institution"}</button>
          </form>
        </section>
      </div>
    </StaffShell>
  );
}
