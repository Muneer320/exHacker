"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Navbar() {
  const pathname = usePathname();
  const isLanding = pathname === "/";

  return (
    <nav className="navbar">
      <div className="container" style={{ display: "flex", alignItems: "center", justifyContent: "space-between", width: "100%" }}>
        {/* Logo */}
        <Link href="/" style={{ display: "flex", alignItems: "center", gap: "10px", textDecoration: "none" }}>
          <div style={{
            width: "28px", height: "28px",
            background: "var(--blue)", borderRadius: "var(--r-sm)",
            display: "flex", alignItems: "center", justifyContent: "center",
          }}>
            <span style={{ fontSize: "12px", fontWeight: 800, color: "#fff", fontFamily: "var(--font-display)" }}>ex</span>
          </div>
          <span style={{ fontFamily: "var(--font-display)", fontWeight: 700, fontSize: "15px", letterSpacing: "-0.02em", color: "var(--text-1)" }}>
            Hacker
          </span>
        </Link>

        {/* Nav links */}
        <div className="hide-mobile" style={{ display: "flex", alignItems: "center", gap: "2px" }}>
          <Link href="/projects" style={{
            padding: "8px 16px", fontSize: "12px", fontWeight: 500, letterSpacing: "0.03em",
            color: "var(--text-2)", textDecoration: "none", transition: "color 0.15s",
          }}
            onMouseEnter={e => { (e.currentTarget).style.color = "var(--text-1)"; }}
            onMouseLeave={e => { (e.currentTarget).style.color = "var(--text-2)"; }}
          >
            Projects
          </Link>
          {!isLanding && (
            <Link href="/" style={{
              padding: "8px 16px", fontSize: "12px", fontWeight: 500, letterSpacing: "0.03em",
              color: "var(--text-2)", textDecoration: "none", transition: "color 0.15s",
            }}
              onMouseEnter={e => { (e.currentTarget).style.color = "var(--text-1)"; }}
              onMouseLeave={e => { (e.currentTarget).style.color = "var(--text-2)"; }}
            >
              New Project
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
}
