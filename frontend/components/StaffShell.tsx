"use client";

import { signOut } from "next-auth/react";

export default function StaffShell({
  role,
  title,
  subtitle,
  email,
  children,
}: {
  role: "Officer" | "Admin";
  title: string;
  subtitle: string;
  email?: string | null;
  children: React.ReactNode;
}) {
  return (
    <div className="staff-layout">
      <aside className="staff-sidebar">
        <a className="staff-brand" href="/" aria-label="Tequami home">
          <span className="staff-brand-symbol" aria-hidden="true">↗</span>
          <span>Tequami</span>
        </a>
        <div className="staff-sidebar-label">WORKSPACE</div>
        <a className="staff-nav-active" href={role === "Admin" ? "/admin" : "/officer"}><span aria-hidden="true">▦</span> Dashboard</a>
        <a className="staff-nav-link" href="/"><span aria-hidden="true">↗</span> Citizen portal</a>
        <div className="staff-sidebar-bottom"><span>{role} access</span><a className="staff-password-link" href="/account">Change password</a><button type="button" onClick={() => signOut({ callbackUrl: role === "Admin" ? "/admin/login" : "/officer/login" })}>Sign out <span aria-hidden="true">↗</span></button></div>
      </aside>
      <div className="staff-main">
        <header className="staff-topbar"><span>Tequami / {role} workspace</span><span className="staff-user">{email || role}</span></header>
        <main className="staff-content"><div className="staff-page-heading"><span className="eyebrow">{role.toUpperCase()} WORKSPACE</span><h1>{title}</h1><p>{subtitle}</p></div>{children}</main>
      </div>
    </div>
  );
}
