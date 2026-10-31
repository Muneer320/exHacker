"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";
import {
  api,
  ApiError,
  selectLease,
  type AISession,
  type Configuration,
} from "@/services/api";

type Target = { provider?: string; model?: string };
type AIContext = {
  config: Configuration | null;
  session: AISession | null;
  open: (target?: Target) => void;
};
const Context = createContext<AIContext>({
  config: null,
  session: null,
  open: () => undefined,
});
export const useAI = () => useContext(Context);

export default function AIProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [config, setConfig] = useState<Configuration | null>(null);
  const [sessions, setSessions] = useState<AISession[]>([]);
  const [active, setActive] = useState<string | null>(null);
  const [target, setTarget] = useState<Target | null>(null);
  const [notice, setNotice] = useState("");
  const current = sessions.find((s) => s.id === active) ?? null;
  const choose = useCallback((id: string | null) => {
    selectLease(id);
    setActive(id);
  }, []);
  const refresh = useCallback(() => {
    void api<Configuration>("/config")
      .then(setConfig)
      .catch(() =>
        setNotice(
          "AI settings are unavailable. Check the project service and retry.",
        ),
      );
  }, []);
  useEffect(() => {
    refresh();
    const reset = () => {
      setSessions([]);
      choose(null);
      setNotice(
        "Workspace changed. Reconnect an API key for future operations.",
      );
    };
    window.addEventListener("exhacker-workspace-changed", reset);
    return () =>
      window.removeEventListener("exhacker-workspace-changed", reset);
  }, [choose, refresh]);
  useEffect(() => {
    let stopped = false;
    const poll = async () => {
      const results = await Promise.all(
        sessions.map(async (session) => {
          if (Date.parse(session.expires_at) <= Date.now()) return null;
          try {
            return await api<AISession>(`/ai/leases/${session.id}`);
          } catch (err) {
            return err instanceof ApiError && err.status === 428
              ? null
              : session;
          }
        }),
      );
      if (stopped) return;
      const remaining = results.filter((s): s is AISession => s !== null);
      if (remaining.length !== sessions.length) {
        setSessions(remaining);
        if (!remaining.some((s) => s.id === active)) {
          choose(null);
          setNotice(
            "Your AI session ended. Saved work is available; reconnect a key to generate more.",
          );
        }
      }
    };
    const timer = setInterval(() => void poll(), 5000);
    return () => {
      stopped = true;
      clearInterval(timer);
    };
  }, [sessions, active, choose]);
  const open = useCallback(
    (value: Target = {}) => {
      setTarget(value);
      refresh();
    },
    [refresh],
  );
  return (
    <Context.Provider value={{ config, session: current, open }}>
      {children}
      <button
        className="ai-session-trigger"
        onClick={() => open()}
        aria-label="AI session settings"
      >
        <span className={current ? "session-dot connected" : "session-dot"} />
        {config?.demo
          ? "Offline demo"
          : current
            ? `${current.provider} · AI session`
            : config?.access_mode === "operator"
              ? "Operator AI"
              : "Connect AI"}
      </button>
      {target && (
        <SessionDialog
          config={config}
          sessions={sessions}
          active={active}
          target={target}
          notice={notice}
          close={() => setTarget(null)}
          choose={choose}
          update={(session, activate = false) => {
            setSessions((previous) => [
              ...previous.filter((s) => s.id !== session.id),
              session,
            ]);
            if (activate) choose(session.id);
            setNotice("");
          }}
          remove={(id) => {
            setSessions((previous) => previous.filter((s) => s.id !== id));
            if (active === id) choose(null);
          }}
          clear={() => {
            setSessions([]);
            choose(null);
          }}
        />
      )}
    </Context.Provider>
  );
}

function SessionDialog({
  config,
  sessions,
  active,
  target,
  notice,
  close,
  choose,
  update,
  remove,
  clear,
}: {
  config: Configuration | null;
  sessions: AISession[];
  active: string | null;
  target: Target;
  notice: string;
  close: () => void;
  choose: (id: string | null) => void;
  update: (session: AISession, activate?: boolean) => void;
  remove: (id: string) => void;
  clear: () => void;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  const [provider, setProvider] = useState(target.provider || "openai");
  const [model, setModel] = useState(target.model || "");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [now, setNow] = useState(() => Date.now());
  const options =
    config?.providers.find((p) => p.id === provider)?.models ?? [];
  const selectedModel = options.find((m) => m.id === model) ?? options[0];
  useEffect(() => {
    const element = dialog.current;
    element?.showModal();
    const timer = setInterval(() => setNow(Date.now()), 1000);
    return () => {
      clearInterval(timer);
      element?.close();
    };
  }, []);
  async function act(operation: () => Promise<void>) {
    setSaving(true);
    setError("");
    try {
      await operation();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not update this AI session.",
      );
    } finally {
      setSaving(false);
    }
  }
  return (
    <dialog
      ref={dialog}
      className="ai-session-dialog"
      onCancel={close}
      aria-labelledby="ai-session-title"
    >
      <div className="section-heading">
        <span className="eyebrow">YOUR MODEL. YOUR KEY.</span>
        <button
          className="text-button"
          onClick={close}
          aria-label="Close AI settings"
        >
          ×
        </button>
      </div>
      <h2 id="ai-session-title">AI sessions</h2>
      <p className="muted">
        Choose who powers your next idea, plan, or conversation.
      </p>
      {error && (
        <p className="notice error" role="alert">
          {error}
        </p>
      )}
      {notice && <p className="notice warning">{notice}</p>}
      {!config ? (
        <p role="status">Loading provider settings…</p>
      ) : config.demo ? (
        <p className="notice warning">
          Offline demonstration. No API key is needed and no live inference or
          research is performed.
        </p>
      ) : config.access_mode === "operator" ? (
        <p className="notice">
          This server uses operator-managed AI. Model: {config.model}.
        </p>
      ) : (
        <>
          <div className="notice">
            <strong>Temporary access, saved progress.</strong>
            <p>
              Your key is sent over the app&apos;s backend connection and held
              only in backend RAM for {Math.round(config.lease_seconds / 60)}{" "}
              minutes. It is cleared from this form on submission. Reloading
              loses browser session references; a server restart requires key
              reentry. Providers bill your account and apply their own data
              policies.
            </p>
          </div>
          <form
            autoComplete="off"
            onSubmit={(event) => {
              event.preventDefault();
              const input = event.currentTarget.elements.namedItem(
                "provider-key",
              ) as HTMLInputElement;
              let key = input.value.trim();
              input.value = "";
              void act(async () => {
                try {
                  const session = await api<AISession>("/ai/leases", "POST", {
                    provider,
                    model: selectedModel?.id,
                    key,
                  });
                  update(session, true);
                } finally {
                  key = "";
                }
              });
            }}
          >
            <div className="form-grid">
              <label>
                AI provider
                <select
                  value={provider}
                  disabled={saving}
                  onChange={(e) => {
                    setProvider(e.target.value);
                    setModel("");
                  }}
                >
                  {config.providers.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                AI model
                <select
                  value={selectedModel?.id ?? ""}
                  disabled={saving}
                  onChange={(e) => setModel(e.target.value)}
                >
                  {options.map((m) => (
                    <option key={m.id} value={m.id}>
                      {m.name}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            {selectedModel && (
              <p className="small muted">
                Context: {selectedModel.context.toLocaleString()} tokens ·
                Maximum output: {selectedModel.output.toLocaleString()} tokens.
                Conservative budget rates: ${selectedModel.input_rate} input / $
                {selectedModel.output_rate} output per million tokens; estimates
                may differ from billing.
              </p>
            )}
            <label>
              Provider API key
              <input
                name="provider-key"
                type="password"
                required
                minLength={8}
                maxLength={512}
                autoComplete="off"
                autoCapitalize="none"
                spellCheck={false}
                placeholder="Paste your provider key"
                disabled={saving}
              />
            </label>
            <p className="small muted">
              Never paste API keys into project briefs or chat. Tavily search is
              managed by the server operator. A session is checked by the
              provider on its first generation request.
            </p>
            <button
              type="submit"
              className="btn btn-lime"
              disabled={saving || !selectedModel}
            >
              {saving ? "Connecting…" : "Start AI session"}
            </button>
          </form>
          <div className="session-list">
            <h3>Sessions in this tab</h3>
            <p className="small muted">
              Switching changes future operations. Running jobs keep their
              original session. Removing a session pauses its active AI calls;
              interrupted work may be billed again when resumed.
            </p>
            {!sessions.length && (
              <p className="muted">No active sessions in this tab.</p>
            )}
            {sessions.map((session) => (
              <div className="session-row" key={session.id}>
                <div>
                  <strong>
                    {session.provider} · {session.model}
                  </strong>
                  <p className="small muted">
                    {Math.max(
                      0,
                      Math.ceil((Date.parse(session.expires_at) - now) / 60000),
                    )}{" "}
                    minutes remaining{" "}
                    {active === session.id ? "· Selected" : ""}
                  </p>
                </div>
                <div className="button-row">
                  <button
                    className="btn btn-ghost"
                    disabled={
                      saving ||
                      active === session.id ||
                      Date.parse(session.expires_at) <= now
                    }
                    onClick={() => choose(session.id)}
                  >
                    Use
                  </button>
                  <button
                    className="text-button"
                    disabled={saving}
                    onClick={() =>
                      void act(async () =>
                        update(
                          await api<AISession>(
                            `/ai/leases/${session.id}/renew`,
                            "POST",
                          ),
                        ),
                      )
                    }
                  >
                    Extend
                  </button>
                  <button
                    className="text-button"
                    disabled={saving}
                    onClick={() =>
                      void act(async () => {
                        await api(`/ai/leases/${session.id}`, "DELETE");
                        remove(session.id);
                      })
                    }
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))}
            <button
              className="text-button"
              disabled={saving}
              onClick={() =>
                void act(async () => {
                  await api("/ai/leases", "DELETE");
                  clear();
                })
              }
            >
              Remove all workspace AI sessions
            </button>
            <p className="small muted">
              Also removes sessions left in server RAM by other tabs or a
              reload.
            </p>
          </div>
        </>
      )}
    </dialog>
  );
}
