import { useEffect, useRef, useState } from "react";
import { api } from "../api";

// Persist reminder settings locally so they survive reloads.
const loadSettings = () => {
  try {
    return JSON.parse(localStorage.getItem("reminderSettings")) || {};
  } catch {
    return {};
  }
};

const DEFAULTS = { work: 25, break: 5, alertsEnabled: true };

function notify(title, body) {
  if ("Notification" in window && Notification.permission === "granted") {
    new Notification(title, { body });
  }
}

export default function Reminders() {
  const [settings, setSettings] = useState({ ...DEFAULTS, ...loadSettings() });
  const [upcoming, setUpcoming] = useState([]);
  const [error, setError] = useState("");

  // Pomodoro state.
  const [phase, setPhase] = useState("work"); // "work" | "break"
  const [secondsLeft, setSecondsLeft] = useState(settings.work * 60);
  const [running, setRunning] = useState(false);
  const timerRef = useRef(null);

  // Persist settings.
  useEffect(() => {
    localStorage.setItem("reminderSettings", JSON.stringify(settings));
  }, [settings]);

  // Load upcoming reminders from the backend.
  useEffect(() => {
    (async () => {
      try {
        setUpcoming(await api.getNextReminders());
      } catch (e) {
        setError(e.message);
      }
    })();
  }, []);

  // Pomodoro countdown loop.
  useEffect(() => {
    if (!running) return;
    timerRef.current = setInterval(() => {
      setSecondsLeft((s) => {
        if (s > 1) return s - 1;
        // Phase finished -> switch and (optionally) alert.
        const nextPhase = phase === "work" ? "break" : "work";
        const nextLen =
          (nextPhase === "work" ? settings.work : settings.break) * 60;
        if (settings.alertsEnabled) {
          notify(
            nextPhase === "break" ? "Time for a break! ☕" : "Back to study 📚",
            nextPhase === "break"
              ? `Take a ${settings.break} min break.`
              : `Focus for ${settings.work} min.`
          );
        }
        setPhase(nextPhase);
        return nextLen;
      });
    }, 1000);
    return () => clearInterval(timerRef.current);
  }, [running, phase, settings]);

  const askPermission = () => {
    if ("Notification" in window) Notification.requestPermission();
  };

  const start = () => {
    askPermission();
    setRunning(true);
  };
  const pause = () => setRunning(false);
  const reset = () => {
    setRunning(false);
    setPhase("work");
    setSecondsLeft(settings.work * 60);
  };

  const mmss = `${String(Math.floor(secondsLeft / 60)).padStart(2, "0")}:${String(
    secondsLeft % 60
  ).padStart(2, "0")}`;

  const dismiss = async (id) => {
    await api.dismissReminder(id);
    setUpcoming(await api.getNextReminders());
  };

  return (
    <div className="grid gap-6 md:grid-cols-2">
      {/* Pomodoro timer */}
      <div className="rounded-xl bg-white p-6 shadow-sm">
        <h2 className="text-lg font-bold">Pomodoro Timer</h2>
        <p className="text-sm text-slate-500">
          Study/break cycles with alerts when each interval ends.
        </p>

        <div className="mt-6 text-center">
          <div
            className={`text-6xl font-mono font-bold ${
              phase === "break" ? "text-emerald-600" : "text-brand-600"
            }`}
          >
            {mmss}
          </div>
          <div className="mt-1 text-sm uppercase tracking-wide text-slate-400">
            {phase === "break" ? "Break" : "Focus"}
          </div>

          <div className="mt-5 flex justify-center gap-2">
            {!running ? (
              <button
                onClick={start}
                className="rounded-lg bg-brand-600 px-5 py-2 font-medium text-white hover:bg-brand-700"
              >
                Start
              </button>
            ) : (
              <button
                onClick={pause}
                className="rounded-lg bg-amber-500 px-5 py-2 font-medium text-white hover:bg-amber-600"
              >
                Pause
              </button>
            )}
            <button
              onClick={reset}
              className="rounded-lg border border-slate-300 px-5 py-2 font-medium hover:bg-slate-50"
            >
              Reset
            </button>
          </div>
        </div>
      </div>

      {/* Settings */}
      <div className="rounded-xl bg-white p-6 shadow-sm">
        <h2 className="text-lg font-bold">Reminder Settings</h2>

        <div className="mt-4 space-y-4 text-sm">
          <label className="flex items-center justify-between gap-4">
            <span>Focus length (minutes)</span>
            <input
              type="number"
              min="1"
              value={settings.work}
              onChange={(e) =>
                setSettings({ ...settings, work: Number(e.target.value) })
              }
              className="w-24 rounded-lg border border-slate-300 px-2 py-1.5"
            />
          </label>
          <label className="flex items-center justify-between gap-4">
            <span>Break length (minutes)</span>
            <input
              type="number"
              min="1"
              value={settings.break}
              onChange={(e) =>
                setSettings({ ...settings, break: Number(e.target.value) })
              }
              className="w-24 rounded-lg border border-slate-300 px-2 py-1.5"
            />
          </label>
          <label className="flex items-center justify-between gap-4">
            <span>Enable study/break alerts</span>
            <input
              type="checkbox"
              checked={settings.alertsEnabled}
              onChange={(e) =>
                setSettings({ ...settings, alertsEnabled: e.target.checked })
              }
              className="h-5 w-5"
            />
          </label>
          <button
            onClick={askPermission}
            className="w-full rounded-lg border border-slate-300 py-2 font-medium hover:bg-slate-50"
          >
            Enable browser notifications
          </button>
        </div>
      </div>

      {/* Upcoming scheduled reminders */}
      <div className="rounded-xl bg-white p-6 shadow-sm md:col-span-2">
        <h2 className="text-lg font-bold">Upcoming Study Alerts</h2>
        {error && (
          <p className="mt-2 rounded bg-red-50 px-3 py-2 text-sm text-red-600">
            {error}
          </p>
        )}
        <ul className="mt-3 divide-y">
          {upcoming.map((r) => (
            <li
              key={r.reminder_id}
              className="flex items-center gap-3 py-2 text-sm"
            >
              <span className="flex-1">
                <span className="font-medium">{r.subject_name}</span> ·{" "}
                {r.unit_name}
              </span>
              <span className="text-slate-500">
                {new Date(r.reminder_time).toLocaleString()}
              </span>
              <button
                onClick={() => dismiss(r.reminder_id)}
                className="rounded bg-slate-200 px-2 py-1 text-xs font-medium hover:bg-slate-300"
              >
                Dismiss
              </button>
            </li>
          ))}
          {upcoming.length === 0 && (
            <li className="py-2 text-sm text-slate-400">
              No upcoming reminders scheduled.
            </li>
          )}
        </ul>
      </div>
    </div>
  );
}
