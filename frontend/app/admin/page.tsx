"use client";

import { useSession } from "next-auth/react";
import { useEffect, useState } from "react";
import StaffShell from "@/components/StaffShell";
import { listPendingInstitutions, approveInstitution, type Institution } from "@/lib/api";

export default function AdminDashboard() {
  const { data: session } = useSession();
  const accessToken = (session as { accessToken?: string })?.accessToken;
  const [pending, setPending] = useState<Institution[]>([]);
  const [loading, setLoading] = useState(true);
  const [approvingId, setApprovingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!accessToken) return;
    listPendingInstitutions(accessToken)
      .then(setPending)
      .catch(() => setError("We couldn't load the approval queue. Please refresh the page."))
      .finally(() => setLoading(false));
  }, [accessToken]);

  const handleApprove = async (id: string) => {
    if (!accessToken || approvingId) return;
    setApprovingId(id);
    setError(null);
    try {
      await approveInstitution(accessToken, id);
      setPending((current) => current.filter((institution) => institution.id !== id));
    } catch {
      setError("Approval failed. Please try again.");
    } finally {
      setApprovingId(null);
    }
  };

  return (
    <StaffShell role="Admin" title="Institution approvals" subtitle="Review incoming institutions before they appear in the service directory." email={session?.user?.email}>
      <div className="staff-stats staff-stats-single"><div><span>AWAITING REVIEW</span><strong>{pending.length}</strong><small>Institutions in your queue</small></div></div>
      <section className="staff-section">
        <div className="staff-section-heading"><div><span className="eyebrow">REVIEW QUEUE</span><h2>Pending institutions</h2></div><span className="staff-count">{pending.length} pending</span></div>
        {error && <div className="staff-error" role="alert">{error}</div>}
        {loading ? <div className="staff-empty"><p>Loading approvals…</p></div> : pending.length === 0 ? <div className="staff-empty"><span aria-hidden="true">✓</span><h3>All caught up</h3><p>There are no institutions waiting for approval.</p></div> : <div className="staff-service-list">{pending.map((inst) => <article key={inst.id} className="staff-service-card staff-approval-card"><div className="staff-service-icon" aria-hidden="true">▦</div><div><h3>{inst.name}</h3><p>{inst.type}{inst.description ? ` · ${inst.description}` : ""}</p></div><button type="button" className="staff-primary-button" disabled={approvingId === inst.id} onClick={() => handleApprove(inst.id)}>{approvingId === inst.id ? "Approving…" : "Approve →"}</button></article>)}</div>}
      </section>
    </StaffShell>
  );
}
