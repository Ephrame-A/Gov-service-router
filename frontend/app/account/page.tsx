"use client";

import { useSession } from "next-auth/react";
import { useState } from "react";
import StaffShell from "@/components/StaffShell";
import { changePassword } from "@/lib/api";

export default function AccountPage() {
  const { data: session } = useSession();
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);
  const role = session?.user?.role === "admin" ? "Admin" : "Officer";

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!session?.accessToken || saving) return;
    setSaving(true);
    setError(null);
    setSaved(false);
    try {
      await changePassword(session.accessToken, currentPassword, newPassword);
      setCurrentPassword("");
      setNewPassword("");
      setSaved(true);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not change password.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <StaffShell role={role} title="Change password" subtitle="Use a new password that you do not use for another account." email={session?.user?.email}>
      <section className="staff-section account-section">
        <form className="staff-form" onSubmit={handleSubmit}>
          {error && <div className="staff-error" role="alert">{error}</div>}
          {saved && <div className="staff-success" role="status">Password changed.</div>}
          <label>Current password<input type="password" autoComplete="current-password" value={currentPassword} onChange={(event) => setCurrentPassword(event.target.value)} required /></label>
          <label>New password<input type="password" autoComplete="new-password" minLength={12} value={newPassword} onChange={(event) => setNewPassword(event.target.value)} required /></label>
          <p className="staff-inline-note">Use at least 12 characters.</p>
          <button className="staff-primary-button" type="submit" disabled={saving || !session?.accessToken}>{saving ? "Saving…" : "Save new password"}</button>
        </form>
      </section>
    </StaffShell>
  );
}
