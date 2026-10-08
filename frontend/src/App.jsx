import { useEffect, useRef, useState } from "react";
import {
  completeSession,
  createSession,
  getErrorMessage,
  getHistory,
  pauseSession,
  resumeSession,
  startSession,
} from "./api";
import "./App.css";

function formatTime(value) {
  if (!value) return "—";

  // Backend timestamps are stored in UTC.
  const utcValue = /(?:Z|[+-]\d{2}:\d{2})$/.test(value)
    ? value
    : `${value}Z`;

  return new Date(utcValue).toLocaleString();
}

export default function App() {
  const [history, setHistory] = useState(null);
  const [title, setTitle] = useState("");
  const [goal, setGoal] = useState("");
  const [duration, setDuration] = useState("25");
  const [reasons, setReasons] = useState({});
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const actionLock = useRef(false);
  const requestNumber = useRef(0);

  async function loadHistory() {
    const currentRequest = ++requestNumber.current;

    try {
      const data = await getHistory();

      if (currentRequest === requestNumber.current) {
        setHistory(data);
        setError("");
      }
    } catch (err) {
      if (currentRequest === requestNumber.current) {
        setError(getErrorMessage(err));
      }
    }
  }

  useEffect(() => {
    loadHistory();

    const timer = setInterval(() => {
      if (!actionLock.current) {
        loadHistory();
      }
    }, 5000);

    return () => {
      clearInterval(timer);
      requestNumber.current += 1;
    };
  }, []);

  async function performAction(action, successMessage) {
    if (actionLock.current) return;

    actionLock.current = true;
    requestNumber.current += 1;
    setBusy(true);
    setError("");
    setMessage("");

    let actionError = "";

    try {
      await action();
      setMessage(successMessage);
    } catch (err) {
      actionError = getErrorMessage(err);
    } finally {
      // Refresh even after a conflict: the session may have ended.
      await loadHistory();

      if (actionError) {
        setError(actionError);
      }

      actionLock.current = false;
      setBusy(false);
    }
  }

  function handleCreate(event) {
    event.preventDefault();

    const minutes = Number(duration);

    if (!title.trim()) {
      setError("Enter a session title.");
      return;
    }

    if (!Number.isInteger(minutes) || minutes < 1 || minutes > 1440) {
      setError("Duration must be a whole number from 1 to 1440.");
      return;
    }

    performAction(async () => {
      await createSession({
        title: title.trim(),
        goal: goal.trim() || null,
        duration: minutes,
      });

      setTitle("");
      setGoal("");
      setDuration("25");
    }, "Session created.");
  }

  function handlePause(session) {
    const reason = (reasons[session.id] || "").trim();

    if (!reason) {
      setError("Enter a reason before pausing.");
      return;
    }

    performAction(async () => {
      const result = await pauseSession(session.id, reason);

      setReasons((current) => ({
        ...current,
        [session.id]: "",
      }));

      setMessage(
        result.status === "interrupted"
          ? "Fourth pause reached. Session interrupted."
          : "Session paused."
      );
    }, "");
  }

  const sessions = history?.sessions || [];
  const completionPercent = (
    (history?.completion_ratio || 0) * 100
  ).toFixed(1);

  return (
    <main className="app">
      <header className="page-header">
        <div>
          <p className="eyebrow">FOCUS · TRACK · IMPROVE</p>
          <h1>Deep Work Tracker</h1>
          <p>Plan focused sessions and understand your interruptions.</p>
        </div>

        <button
          type="button"
          disabled={busy}
          onClick={loadHistory}
        >
          Refresh
        </button>
      </header>

      {error && <div className="alert error" role="alert">{error}</div>}
      {message && (
        <div className="alert success" role="status">{message}</div>
      )}

      <section className="stats" aria-label="Session statistics">
        <div className="stat">
          <span>Total sessions</span>
          <strong>{history?.total_sessions ?? "—"}</strong>
        </div>
        <div className="stat">
          <span>Finished sessions</span>
          <strong>{history?.finished_sessions ?? "—"}</strong>
        </div>
        <div className="stat">
          <span>Completed on time</span>
          <strong>{history?.completed_sessions ?? "—"}</strong>
        </div>
        <div className="stat">
          <span>Completion rate</span>
          <strong>{history ? `${completionPercent}%` : "—"}</strong>
        </div>
      </section>

      <section className="panel">
        <h2>Create a session</h2>

        <form className="create-form" onSubmit={handleCreate}>
          <label>
            Title
            <input
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              placeholder="What will you focus on?"
              maxLength={200}
              required
              disabled={busy}
            />
          </label>

          <label>
            Duration in minutes
            <input
              type="number"
              value={duration}
              onChange={(event) => setDuration(event.target.value)}
              min={1}
              max={1440}
              step={1}
              required
              disabled={busy}
            />
          </label>

          <label className="full-width">
            Goal (optional)
            <textarea
              value={goal}
              onChange={(event) => setGoal(event.target.value)}
              placeholder="Describe the outcome you want."
              maxLength={2000}
              rows={2}
              disabled={busy}
            />
          </label>

          <button className="primary" type="submit" disabled={busy}>
            {busy ? "Please wait…" : "Create session"}
          </button>
        </form>
      </section>

      <section className="history-section">
        <h2>Your sessions</h2>
        <p className="muted">
          Updates every 5 seconds. Elapsed time includes breaks.
          Completion rate measures on-time completions among ended sessions.
        </p>

        {!history && !error && <p>Loading sessions…</p>}
        {history && sessions.length === 0 && (
          <p>No sessions yet. Create your first one above.</p>
        )}

        <div className="session-list">
          {sessions.map((session) => (
            <article className="panel session-card" key={session.id}>
              <div className="session-heading">
                <div>
                  <p className="muted">Session #{session.id}</p>
                  <h3>{session.title}</h3>
                </div>
                <span className={`badge ${session.status}`}>
                  {session.status}
                </span>
              </div>

              {session.goal && <p>{session.goal}</p>}

              <div className="session-meta">
                <span>Planned: {session.scheduled_duration} min</span>
                <span>Elapsed: {session.elapsed_minutes} min</span>
                <span>Pauses: {session.pause_count}</span>
              </div>

              <p className="muted">
                Started: {formatTime(session.start_time)}
                <br />
                Ended: {formatTime(session.end_time)}
              </p>

              {session.status === "scheduled" && (
                <button
                  className="primary"
                  disabled={busy}
                  onClick={() =>
                    performAction(
                      () => startSession(session.id),
                      "Session started."
                    )
                  }
                >
                  Start
                </button>
              )}

              {session.status === "active" && (
                <div className="session-actions">
                  <label>
                    Pause reason
                    <input
                      value={reasons[session.id] || ""}
                      onChange={(event) =>
                        setReasons((current) => ({
                          ...current,
                          [session.id]: event.target.value,
                        }))
                      }
                      placeholder="Why are you taking a break?"
                      maxLength={500}
                      disabled={busy}
                    />
                  </label>

                  <div className="button-row">
                    <button
                      disabled={busy}
                      onClick={() => handlePause(session)}
                    >
                      Pause
                    </button>

                    <button
                      className="primary"
                      disabled={busy}
                      onClick={() =>
                        performAction(async () => {
                          const result = await completeSession(session.id);
                          setMessage(
                            result.status === "overdue"
                              ? "Session ended after its time allowance."
                              : "Session completed on time."
                          );
                        }, "")
                      }
                    >
                      Complete
                    </button>
                  </div>
                </div>
              )}

              {session.status === "paused" && (
                <button
                  className="primary"
                  disabled={busy}
                  onClick={() =>
                    performAction(
                      () => resumeSession(session.id),
                      "Session resumed."
                    )
                  }
                >
                  Resume
                </button>
              )}

              {session.interruptions.length > 0 && (
                <details className="interruptions">
                  <summary>
                    Pause history ({session.pause_count})
                  </summary>
                  <ul>
                    {session.interruptions.map((item) => (
                      <li key={item.id}>
                        <span>{item.reason}</span>
                        <small>{formatTime(item.pause_time)}</small>
                      </li>
                    ))}
                  </ul>
                </details>
              )}
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}