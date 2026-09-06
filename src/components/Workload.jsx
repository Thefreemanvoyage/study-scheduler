import { useEffect, useState } from "react";
import { api } from "../api";

// Burden index > 1 means you must now study more per day than planned.
function burdenBadge(idx) {
  if (idx <= 1.05)
    return { label: "On track", cls: "bg-emerald-100 text-emerald-700" };
  if (idx <= 1.3)
    return { label: "Slightly behind", cls: "bg-amber-100 text-amber-700" };
  return { label: "Overloaded", cls: "bg-rose-100 text-rose-700" };
}

export default function Workload() {
  const [rows, setRows] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        setRows(await api.getWorkload());
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-xl font-bold">Adaptive Workload</h2>
        <p className="text-sm text-slate-500">
          When tasks are skipped, remaining hours are re-spread across the days
          you have left. The <strong>burden index</strong> shows how much
          heavier each day has become.
        </p>
      </div>

      {error && (
        <p className="rounded bg-red-50 px-3 py-2 text-sm text-red-600">
          {error}
        </p>
      )}

      {loading ? (
        <p className="text-slate-500">Loading…</p>
      ) : rows.length === 0 ? (
        <p className="text-slate-500">No subjects to analyse yet.</p>
      ) : (
        <div className="overflow-x-auto rounded-xl bg-white shadow-sm">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500">
              <tr>
                <th className="px-4 py-3">Subject</th>
                <th className="px-4 py-3">Remaining</th>
                <th className="px-4 py-3">Days left</th>
                <th className="px-4 py-3">Planned/day</th>
                <th className="px-4 py-3">Now needed/day</th>
                <th className="px-4 py-3">Skipped</th>
                <th className="px-4 py-3">Burden</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {rows.map((r) => {
                const badge = burdenBadge(r.burden_index);
                return (
                  <tr key={r.subject_id}>
                    <td className="px-4 py-3 font-medium">{r.subject_name}</td>
                    <td className="px-4 py-3">{r.remaining_hours} h</td>
                    <td className="px-4 py-3">{r.remaining_days}</td>
                    <td className="px-4 py-3">{r.original_daily_hours} h</td>
                    <td className="px-4 py-3 font-semibold">
                      {r.recommended_daily_hours} h
                    </td>
                    <td className="px-4 py-3 text-rose-600">
                      {r.skipped_hours} h
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <span className="font-mono">
                          {r.burden_index.toFixed(2)}×
                        </span>
                        <span
                          className={`rounded-full px-2 py-0.5 text-xs font-medium ${badge.cls}`}
                        >
                          {badge.label}
                        </span>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
