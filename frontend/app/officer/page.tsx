"use client";

import { useSession } from "next-auth/react";
import { useEffect, useState } from "react";
import StaffShell from "@/components/StaffShell";
import { listDepartments, listServices, createService, refreshServiceEmbedding, type Department, type Service } from "@/lib/api";

const emptyForm = { department_id: "", name: "", description: "", example_phrasings: "", required_documents: "" };

export default function OfficerDashboard() {
  const { data: session } = useSession();
  const accessToken = (session as { accessToken?: string })?.accessToken;
  const institutionId = (session?.user as { institutionId?: string })?.institutionId;
  const role = (session?.user as { role?: string })?.role;
  const [departments, setDepartments] = useState<Department[]>([]);
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState(emptyForm);

  useEffect(() => {
    if (!accessToken || !institutionId) return;
    Promise.all([listDepartments(accessToken, institutionId), listServices(accessToken, institutionId)])
      .then(([depts, svcs]) => {
        setDepartments(depts);
        setServices(svcs);
        if (depts.length > 0) setForm((current) => ({ ...current, department_id: depts[0].id }));
      })
      .catch(() => setError("We couldn't load your services. Please refresh the page."))
      .finally(() => setLoading(false));
  }, [accessToken, institutionId]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!accessToken || saving) return;
    setSaving(true);
    setError(null);
    try {
      const svc = await createService(accessToken, {
        department_id: form.department_id,
        name: form.name.trim(),
        description: form.description.trim(),
        example_phrasings: form.example_phrasings.split("\n").map((line) => line.trim()).filter(Boolean),
        required_documents: form.required_documents.split("\n").map((line) => line.trim()).filter(Boolean),
      });
      setServices((current) => [...current, svc]);
      setShowForm(false);
      setForm({ ...emptyForm, department_id: departments[0]?.id || "" });
      try {
        await refreshServiceEmbedding(accessToken, svc.id);
        setServices((current) => current.map((item) => item.id === svc.id ? { ...item, has_embedding: true } : item));
      } catch {
        setError("The service was created, but search indexing did not finish. Please try again later.");
      }
    } catch {
      setError("We couldn't create the service. Please check the details and try again.");
    } finally {
      setSaving(false);
    }
  };

  if (role === "admin") {
    return <StaffShell role="Admin" title="Your workspace" subtitle="Institution approvals are managed in the admin dashboard." email={session?.user?.email}><div className="staff-empty"><span aria-hidden="true">↗</span><h2>Head to the approval queue</h2><p>Review pending institution registrations and keep the service directory moving.</p><a className="staff-primary-link" href="/admin">Open admin dashboard →</a></div></StaffShell>;
  }

  return (
    <StaffShell role="Officer" title="Your services" subtitle="Keep service information clear and ready for the people who need it." email={session?.user?.email}>
      <div className="staff-stats"><div><span>TOTAL SERVICES</span><strong>{services.length}</strong><small>Listed in your institution</small></div><div><span>SEARCHABLE</span><strong>{services.filter((svc) => svc.has_embedding).length}</strong><small>Ready for citizen searches</small></div><div><span>DEPARTMENTS</span><strong>{departments.length}</strong><small>Organizing your services</small></div></div>
      <section className="staff-section">
        <div className="staff-section-heading"><div><span className="eyebrow">DIRECTORY</span><h2>Service listings</h2></div><button type="button" className="staff-primary-button" onClick={() => setShowForm(!showForm)}>{showForm ? "Close form" : "+ Add service"}</button></div>
        {error && <div className="staff-error" role="alert">{error}</div>}
        {showForm && <form onSubmit={handleCreate} className="staff-form">
          <div className="staff-form-title"><h3>Add a new service</h3><p>Good descriptions help citizens find the right office.</p></div>
          <div className="staff-form-grid"><label>Department<select value={form.department_id} onChange={(e) => setForm({ ...form, department_id: e.target.value })} required>{departments.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}</select></label><label>Service name<input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="e.g. Business license renewal" required /></label></div>
          <label>Description<textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Describe who this service is for and what it provides" rows={3} required /></label>
          <div className="staff-form-grid"><label>Example requests <small>One per line</small><textarea value={form.example_phrasings} onChange={(e) => setForm({ ...form, example_phrasings: e.target.value })} rows={4} placeholder="I need to renew my license" /></label><label>Required documents <small>One per line</small><textarea value={form.required_documents} onChange={(e) => setForm({ ...form, required_documents: e.target.value })} rows={4} placeholder="Current license" /></label></div>
          <button className="staff-primary-button" type="submit" disabled={saving || departments.length === 0}>{saving ? "Creating service…" : "Create service"}</button>
        </form>}
        {loading ? <div className="staff-empty"><p>Loading your services…</p></div> : services.length === 0 ? <div className="staff-empty"><span aria-hidden="true">▦</span><h3>No services yet</h3><p>Add your first service to help citizens find your institution.</p></div> : <div className="staff-service-list">{services.map((svc) => <article key={svc.id} className="staff-service-card"><div className="staff-service-icon" aria-hidden="true">▦</div><div><h3>{svc.name}</h3><p>{svc.description}</p></div><span className={`staff-status ${svc.has_embedding ? "is-ready" : "is-pending"}`}>{svc.has_embedding ? "Searchable" : "Index pending"}</span></article>)}</div>}
      </section>
    </StaffShell>
  );
}
