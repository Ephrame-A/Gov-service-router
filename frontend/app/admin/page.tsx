"use client";

import { useSession, signOut } from "next-auth/react";
import { useEffect, useState } from "react";
import {
  listPendingInstitutions,
  approveInstitution,
  type Institution,
} from "@/lib/api";

export default function AdminDashboard() {
  const { data: session } = useSession();
  const accessToken = (session as { accessToken?: string })?.accessToken;
  const [pending, setPending] = useState<Institution[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!accessToken) return;
    listPendingInstitutions(accessToken)
      .then(setPending)
      .finally(() => setLoading(false));
  }, [accessToken]);

  const handleApprove = async (id: string) => {
    if (!accessToken) return;
    await approveInstitution(accessToken, id);
    setPending((prev) => prev.filter((i) => i.id !== id));
  };

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-xl sm:p-8">
        <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-slate-900">Admin Dashboard</h1>
            <p className="text-sm text-slate-600">Institution approval queue</p>
          </div>
          <button onClick={() => signOut({ callbackUrl: "/officer/login" })} className="rounded-full border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-50">
            Sign out
          </button>
        </div>

        {loading ? (
          <div className="rounded-2xl bg-slate-50 p-6 text-center text-slate-500">Loading approvals…</div>
        ) : pending.length === 0 ? (
          <div className="rounded-[24px] border border-slate-200 bg-slate-50 p-8 text-center text-slate-500">
            No institutions pending approval
          </div>
        ) : (
          <div className="space-y-3">
            {pending.map((inst) => (
              <div key={inst.id} className="flex flex-col gap-3 rounded-[20px] border border-slate-200 bg-white p-5 shadow-sm sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <h3 className="font-semibold text-slate-900">{inst.name}</h3>
                  <p className="text-sm text-slate-600">{inst.type} — {inst.description}</p>
                </div>
                <button onClick={() => handleApprove(inst.id)} className="rounded-full bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700">
                  Approve
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
