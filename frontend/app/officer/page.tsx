"use client";

import { useSession, signOut } from "next-auth/react";
import { useEffect, useState } from "react";
import {
  listDepartments,
  listServices,
  createService,
  refreshServiceEmbedding,
  type Department,
  type Service,
} from "@/lib/api";

export default function OfficerDashboard() {
  const { data: session } = useSession();
  const accessToken = (session as { accessToken?: string })?.accessToken;
  const institutionId = (session?.user as { institutionId?: string })?.institutionId;
  const role = (session?.user as { role?: string })?.role;

  const [departments, setDepartments] = useState<Department[]>([]);
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    department_id: "",
    name: "",
    description: "",
    example_phrasings: "",
    required_documents: "",
  });

  useEffect(() => {
    if (!accessToken || !institutionId) return;
    Promise.all([
      listDepartments(accessToken, institutionId),
      listServices(accessToken, institutionId),
    ])
      .then(([depts, svcs]) => {
        setDepartments(depts);
        setServices(svcs);
        if (depts.length > 0) {
          setForm((f) => ({ ...f, department_id: depts[0].id }));
        }
      })
      .finally(() => setLoading(false));
  }, [accessToken, institutionId]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!accessToken) return;
    const svc = await createService(accessToken, {
      department_id: form.department_id,
      name: form.name,
      description: form.description,
      example_phrasings: form.example_phrasings.split("\n").filter(Boolean),
      required_documents: form.required_documents.split("\n").filter(Boolean),
    });
    await refreshServiceEmbedding(accessToken, svc.id);
    setServices((prev) => [...prev, { ...svc, has_embedding: true }]);
    setShowForm(false);
    setForm({ department_id: departments[0]?.id || "", name: "", description: "", example_phrasings: "", required_documents: "" });
  };

  if (role === "admin") {
    return (
      <div className="mx-auto flex min-h-screen max-w-5xl items-center justify-center px-4 py-12">
        <div className="w-full rounded-[28px] border border-slate-200 bg-white p-8 shadow-xl">
          <p className="text-lg font-semibold text-slate-900">You are signed in as admin.</p>
          <p className="mt-2 text-slate-600">Manage institution approvals and review pending requests from here.</p>
          <a href="/admin" className="mt-6 inline-flex rounded-full bg-sky-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-sky-700">
            Go to admin dashboard →
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-xl sm:p-8">
        <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-slate-900">Officer Dashboard</h1>
            <p className="text-sm text-slate-600">{session?.user?.email}</p>
          </div>
          <button onClick={() => signOut({ callbackUrl: "/officer/login" })} className="rounded-full border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-50">
            Sign out
          </button>
        </div>

        {loading ? (
          <div className="rounded-2xl bg-slate-50 p-6 text-center text-slate-500">Loading your services…</div>
        ) : (
          <>
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-slate-900">Services ({services.length})</h2>
              <button onClick={() => setShowForm(!showForm)} className="rounded-full bg-sky-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-sky-700">
                {showForm ? "Cancel" : "+ Add Service"}
              </button>
            </div>

            {showForm && (
              <form onSubmit={handleCreate} className="mb-6 space-y-3 rounded-[24px] border border-slate-200 bg-slate-50 p-5">
                <select value={form.department_id} onChange={(e) => setForm({ ...form, department_id: e.target.value })} className="w-full rounded-2xl border border-slate-300 bg-white px-3 py-2.5" required>
                  {departments.map((d) => (
                    <option key={d.id} value={d.id}>{d.name}</option>
                  ))}
                </select>
                <input placeholder="Service name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="w-full rounded-2xl border border-slate-300 bg-white px-3 py-2.5" required />
                <textarea placeholder="Description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="w-full rounded-2xl border border-slate-300 bg-white px-3 py-2.5" rows={2} required />
                <textarea placeholder="Example phrasings (one per line)" value={form.example_phrasings} onChange={(e) => setForm({ ...form, example_phrasings: e.target.value })} className="w-full rounded-2xl border border-slate-300 bg-white px-3 py-2.5" rows={3} />
                <textarea placeholder="Required documents (one per line)" value={form.required_documents} onChange={(e) => setForm({ ...form, required_documents: e.target.value })} className="w-full rounded-2xl border border-slate-300 bg-white px-3 py-2.5" rows={2} />
                <button type="submit" className="rounded-full bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700">
                  Create & Generate Embedding
                </button>
              </form>
            )}

            <div className="space-y-3">
              {services.map((svc) => (
                <div key={svc.id} className="rounded-[20px] border border-slate-200 bg-white p-4 shadow-sm">
                  <div className="flex items-center justify-between gap-3">
                    <h3 className="font-semibold text-slate-900">{svc.name}</h3>
                    <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${svc.has_embedding ? "bg-emerald-100 text-emerald-700" : "bg-amber-100 text-amber-700"}`}>
                      {svc.has_embedding ? "Searchable" : "No embedding"}
                    </span>
                  </div>
                  <p className="mt-1 text-sm text-slate-600">{svc.description}</p>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
