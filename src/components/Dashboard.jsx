import { useEffect, useState } from "react";
import { api } from "../api";

// Colour the progress bar by completion level.
function barColor(pct) {
  if (pct >= 80) return "bg-emerald-500";
  if (pct >= 40) return "bg-amber-500";
  return "bg-rose-500";
}

export default function Dashboard() {
  const [progress, setProgress] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [newSubject, setNewSubject] = useState("");

  const load = async () => {
    setError("");
    try {
      setProgress(await api.getProgress());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const addSubject = async (e) => {
    e.preventDefault();
    if (!newSubject.trim()) return;
    try {
      await api.createSubject({ name: newSubject.trim() });
      setNewSubject("");
      load();
    } catch (e) {
      setError(e.message);
    }
  };

  const removeSubject = async (id) => {
    if (!confirm("Delete this subject and all its units/tasks?")) return;
    await api.deleteSubject(id);
    load();
  };

  const overall =
    progress.length > 0
      ? Math.round(
          progress.reduce((s, p) => s + p.completion_percent, 0) /
            progress.length
        )
      : 0;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">Progress Dashboard</h2>
        <div className="text-sm text-slate-500">
          Overall completion:{" "}
          <span className="font-semibold text-slate-800">{overall}%</span>
        </div>
      </div>

      {/* Add subject */}
      <form onSubmit={addSubject} className="flex gap-2">
        <input
          className="flex-1 rounded-lg border border-slate-300 px-3 py-2 focus:border-brand-500 focus:outline-none"
          placeholder="Add a subject (e.g. Costing Methods)"
          value={newSubject}
          onChange={(e) => setNewSubject(e.target.value)}
        />
        <button className="rounded-lg bg-brand-600 px-4 py-2 font-medium text-white hover:bg-brand-700">
          Add
        </button>
      </form>

      {error && (
        <p className="rounded bg-red-50 px-3 py-2 text-sm text-red-600">
          {error}
        </p>
      )}

      {loading ? (
        <p className="text-slate-500">Loading…</p>
      ) : progress.length === 0 ? (
        <p className="text-slate-500">
          No subjects yet. Add one above (or run the backend seed script).
        </p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {progress.map((p) => (
            <div
              key={p.subject_id}
              className="rounded-xl bg-white p-5 shadow-sm"
            >
              <div className="flex items-start justify-between">
                <h3 className="font-semibold">{p.subject_name}</h3>
                <button
                  onClick={() => removeSubject(p.subject_id)}
                  className="text-xs text-slate-400 hover:text-rose-500"
                >
                  Delete
                </button>
              </div>

              <div className="mt-3 h-3 w-full overflow-hidden rounded-full bg-slate-200">
                <div
                  className={`h-full ${barColor(
                    p.completion_percent
                  )} transition-all`}
                  style={{ width: `${p.completion_percent}%` }}
                />
              </div>

              <div className="mt-2 flex justify-between text-sm text-slate-500">
                <span>{p.completion_percent}% complete</span>
                <span>
                  {p.completed_hours}/{p.planned_hours} hrs
                </span>
              </div>

              <div className="mt-2 flex gap-4 text-xs text-slate-400">
                <span>✅ {p.completed_tasks} done</span>
                <span>⏭️ {p.skipped_tasks} skipped</span>
                <span>📋 {p.total_tasks} total</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
