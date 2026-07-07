"use client";

import { createContext, useContext, useState, useCallback, type ReactNode } from "react";

// ─── Types ────────────────────────────────────────────────────────────────────

export type ToastType = "success" | "error" | "info" | "warning";

export interface Toast {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
}

interface ToastContextType {
  toasts: Toast[];
  addToast: (t: Omit<Toast, "id">) => string;
  removeToast: (id: string) => void;
  clearToasts: () => void;
}

const ToastContext = createContext<ToastContextType | null>(null);

export function useToast(): ToastContextType {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within ToastProvider");
  return ctx;
}

// ─── Provider ─────────────────────────────────────────────────────────────────

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  const addToast = useCallback((t: Omit<Toast, "id">): string => {
    const id = `t-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`;
    const toast: Toast = { ...t, id };
    setToasts(prev => [...prev, toast]);
    const dur = t.duration || (t.type === "error" ? 6000 : 3000);
    setTimeout(() => removeToast(id), dur);
    return id;
  }, [removeToast]);

  const clearToasts = useCallback(() => setToasts([]), []);

  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast, clearToasts }}>
      {children}
      <ToastContainer />
    </ToastContext.Provider>
  );
}

// ─── Container ────────────────────────────────────────────────────────────────

const ICONS: Record<ToastType, string> = {
  success: "✓",
  error: "✕",
  info: "i",
  warning: "⚠",
};

const COLORS: Record<ToastType, { border: string; bg: string; text: string }> = {
  success: { border: "rgba(194,255,77,0.3)", bg: "rgba(194,255,77,0.08)", text: "var(--lime)" },
  error: { border: "rgba(239,68,68,0.3)", bg: "rgba(239,68,68,0.08)", text: "var(--error)" },
  info: { border: "rgba(61,124,246,0.3)", bg: "rgba(61,124,246,0.08)", text: "var(--blue-light)" },
  warning: { border: "rgba(245,158,11,0.3)", bg: "rgba(245,158,11,0.08)", text: "var(--warning)" },
};

function ToastContainer() {
  const { toasts, removeToast } = useToast();

  return (
    <div style={{
      position: "fixed", bottom: "24px", right: "24px", zIndex: 1100,
      display: "flex", flexDirection: "column", gap: "8px", maxWidth: "360px",
    }}>
      {toasts.map(t => {
        const c = COLORS[t.type];
        return (
          <div
            key={t.id}
            className="anim-fade-up"
            style={{
              padding: "12px 16px", borderRadius: "var(--r-md)",
              border: `1px solid ${c.border}`,
              background: c.bg, backdropFilter: "blur(8px)",
              display: "flex", gap: "10px", alignItems: "flex-start",
              cursor: "pointer",
            }}
            onClick={() => removeToast(t.id)}
            role="alert"
          >
            <span style={{ color: c.text, fontWeight: 700, fontSize: "13px", flexShrink: 0, marginTop: "1px" }}>
              {ICONS[t.type]}
            </span>
            <div style={{ flex: 1 }}>
              <p style={{ fontSize: "12px", fontWeight: 600, color: "var(--text-1)" }}>{t.title}</p>
              {t.message && <p style={{ fontSize: "11px", color: "var(--text-2)", marginTop: "2px" }}>{t.message}</p>}
            </div>
          </div>
        );
      })}
    </div>
  );
}
