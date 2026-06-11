"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Navbar() {
  const path = usePathname();
  const isHome = path === "/";

  return (
    <nav className="navbar">
      <div className="container" style={{ display: "flex", alignItems: "center", justifyContent: "space-between", width: "100%" }}>
        {/* Logo */}
        <Link href="/" style={{ display: "flex", alignItems: "center", gap: "8px", textDecoration: "none" }}>
          <div style={{
            width: "28px", height: "28px",
            background: "var(--blue)",
            borderRadius: "4px",
            display: "flex", alignItems: "center", justifyContent: "center",
          }}>
            <span style={{ fontSize: "12px", fontWeight: 800, color: "#fff", fontFamily: "var(--font-display)" }}>ex</span>
          </div>
          <span style={{ fontFamily: "var(--font-display)", fontWeight: 700, fontSize: "15px", letterSpacing: "-0.02em", color: "var(--text-1)" }}>
            Hacker
          </span>
        </Link>

        {/* Center links (hidden on mobile) */}
        <div className="hide-mobile" style={{ display: "flex", alignItems: "center", gap: "2px" }}>
          {[
            { href: "/", label: "Home" },
            { href: "/generate", label: "New Project" },
          ].map(({ href, label }) => (
            <Link
              key={href}
              href={href}
              style={{
                padding: "6px 14px",
                fontSize: "13px",
                fontWeight: 500,
                color: path === href ? "var(--text-1)" : "var(--text-3)",
                textDecoration: "none",
                borderRadius: "4px",
                background: path === href ? "var(--surface-2)" : "transparent",
                transition: "all 0.15s",
              }}
            >
              {label}
            </Link>
          ))}
        </div>

        {/* CTA */}
        <Link href="/generate" className="btn btn-primary" style={{ textDecoration: "none", padding: "8px 18px", fontSize: "12px" }}>
          <span style={{ fontSize: "10px" }}>◆</span>
          New Project
        </Link>
      </div>
    </nav>
  );
}
