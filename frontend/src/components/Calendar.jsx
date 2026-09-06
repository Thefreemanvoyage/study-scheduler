import { useEffect, useMemo, useState } from "react";
import { api } from "../api";

// ---- date helpers (local, no external lib) ----
const iso = (d) => d.toISOString().slice(0, 10); // YYYY-MM-DD
const startOfMonth = (d) => new Date(d.getFullYear(), d.getMonth(), 1);
const addMonths = (d, n) => new Date(d.getFullYear(), d.getMonth() + n, 1);
const WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

const statusStyle = {
  pending: "bg-brand-50 text-brand-700 border-brand-200",
  completed: "bg-emerald-50 text-emerald-700 border-emerald-200 line-through",
  skipped: "bg-rose-50 text-rose-700 border-rose-200",
};

export default function Calendar() {
  const [cursor, setCursor] = useState(startOfMonth(new Date()));
  const [subjects, setSubjects] = useState([]);
  const [units, setUnits] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [error, setError] = useState("");
  const [selectedDay, setSelectedDay] = useState(null);

  // New-task form state.
  const [unitId, setUnitId] = useState("");
  const [hours, setHours] = useState(2);

  const load = async () => {
    setError("");
    try {
      const [subj, un, tk] = await Promise.all([
        api.getSubjects(),
        api.getUnits(),
        api.getTasks(),
      ]);
      setSubjects(subj);
      setUnits(un);
      setTasks(tk);
      if (!unitId && un.length) setUnitId(String(un[0].id));
    } catch (e) {
      setError(e.message);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Lookup maps for names.
  const unitById = useMemo(
    () => Object.fromEntries(units.map((u) => [u.id, u])),
    [units]
  );
  const subjectById = useMemo(
    () => Object.fromEntries(subjects.map((s) => [s.id, s])),
    [subjects]
  );

  // Group tasks by ISO date.
  const tasksByDate = useMemo(() => {
    const map = {};
    for (const t of tasks) (map[t.date] ??= []).push(t);
    return map;
  }, [tasks]);

  // Build the 6x7 grid of days for the visible month.
  const days = useMemo(() => {
    const first = startOfMonth(cursor);
    const gridStart = new Date(first);
    gridStart.setDate(first.getDate() - first.getDay()); // back to Sunday
    return Array.from({ length: 42 }, (_, i) => {
      const d = new Date(gridStart);
      d.setDate(gridStart.getDate() + i);
      return d;
    });
  }, [cursor]);

  const addTask = async (e) => {
    e.preventDefault();
    if (!unitId || !selectedDay) return;
    try {
      await api.createTask({
        unit_id: Number(unitId),
        date: selectedDay,
        planned_hours: Number(hours),
      });
      await load();
    } catch (e) {
      setError(e.message);
    }
  };

  const act = async (fn, id) => {
    try {
      await fn(id);
      await load();
    } catch (e) {
      setError(e.message);
    }
  };

  const monthLabel = cursor.toLocaleString("default", {
    month: "long",
    year: "numeric",
  });
  const todayIso = iso(new Date());

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">Study Calendar</h2>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setCursor(addMonths(cursor, -1))}
            className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm hover:bg-slate-50"
          >
            ‹ Prev
          </button>
          <span className="w-40 text-center font-medium">{monthLabel}</span>
          <button
            onClick={() => setCursor(addMonths(cursor, 1))}
            className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm hover:bg-slate-50"
          >
            Next ›
          </button>
        </div>
      </div>

      {error && (
        <p className="rounded bg-red-50 px-3 py-2 text-sm text-red-600">
          {error}
        </p>
      )}

      {subjects.length === 0 && (
        <p className="text-slate-500">
          Add subjects and units first (Dashboard / seed script) to schedule
          tasks.
        </p>
      )}

      {/* Calendar grid */}
      <div className="grid grid-cols-7 gap-px overflow-hidden rounded-xl bg-slate-200 text-sm shadow-sm">
        {WEEKDAYS.map((w) => (
          <div
            key={w}
            className="bg-slate-50 py-2 text-center text-xs font-semibold text-slate-500"
          >
            {w}
          </div>
        ))}
        {days.map((d) => {
          const key = iso(d);
          const inMonth = d.getMonth() === cursor.getMonth();
          const dayTasks = tasksByDate[key] || [];
          return (
            <button
              key={key}
              onClick={() => setSelectedDay(key)}
              className={`min-h-[92px] bg-white p-1.5 text-left align-top transition hover:bg-brand-50 ${
                inMonth ? "" : "bg-slate-50 text-slate-400"
              } ${selectedDay === key ? "ring-2 ring-brand-500" : ""}`}
            >
              <div className="flex justify-between">
                <span
                  className={`text-xs font-medium ${
                    key === todayIso
                      ? "rounded-full bg-brand-600 px-1.5 text-white"
                      : ""
                  }`}
                >
                  {d.getDate()}
                </span>
              </div>
              <div className="mt-1 space-y-0.5">
                {dayTasks.slice(0, 3).map((t) => {
                  const u = unitById[t.unit_id];
                  const s = u ? subjectById[u.subject_id] : null;
                  return (
                    <div
                      key={t.id}
                      className={`truncate rounded border px-1 py-0.5 text-[10px] ${statusStyle[t.status]}`}
                      title={`${s?.name || ""} · ${u?.name || ""} (${t.planned_hours}h)`}
                    >
                      {s?.name?.split(" ")[0]}: {u?.name}
                    </div>
                  );
                })}
                {dayTasks.length > 3 && (
                  <div className="text-[10px] text-slate-400">
                    +{dayTasks.length - 3} more
                  </div>
                )}
              </div>
            </button>
          );
        })}
      </div>

      {/* Day detail panel */}
      {selectedDay && (
        <div className="rounded-xl bg-white p-5 shadow-sm">
          <h3 className="font-semibold">Tasks on {selectedDay}</h3>

          <ul className="mt-3 divide-y">
            {(tasksByDate[selectedDay] || []).map((t) => {
              const u = unitById[t.unit_id];
              const s = u ? subjectById[u.subject_id] : null;
              return (
                <li
                  key={t.id}
                  className="flex flex-wrap items-center gap-2 py-2 text-sm"
                >
                  <span className="flex-1">
                    <span className="font-medium">{s?.name}</span> · {u?.name}{" "}
                    <span className="text-slate-400">({t.planned_hours}h)</span>
                  </span>
                  <span
                    className={`rounded border px-2 py-0.5 text-xs ${statusStyle[t.status]}`}
                  >
                    {t.status}
                  </span>
                  <button
                    onClick={() => act(api.completeTask, t.id)}
                    className="rounded bg-emerald-500 px-2 py-1 text-xs font-medium text-white hover:bg-emerald-600"
                  >
                    Complete
                  </button>
                  <button
                    onClick={() => act(api.skipTask, t.id)}
                    className="rounded bg-amber-500 px-2 py-1 text-xs font-medium text-white hover:bg-amber-600"
                  >
                    Skip
                  </button>
                  <button
                    onClick={() => act(api.deleteTask, t.id)}
                    className="rounded bg-slate-200 px-2 py-1 text-xs font-medium hover:bg-slate-300"
                  >
                    Delete
                  </button>
                </li>
              );
            })}
            {(tasksByDate[selectedDay] || []).length === 0 && (
              <li className="py-2 text-sm text-slate-400">
                No tasks scheduled.
              </li>
            )}
          </ul>

          {/* Add task */}
          {units.length > 0 && (
            <form
              onSubmit={addTask}
              className="mt-4 flex flex-wrap items-end gap-2 border-t pt-4"
            >
              <div>
                <label className="block text-xs font-medium text-slate-500">
                  Unit
                </label>
                <select
                  value={unitId}
                  onChange={(e) => setUnitId(e.target.value)}
                  className="mt-1 rounded-lg border border-slate-300 px-2 py-1.5 text-sm"
                >
                  {units.map((u) => (
                    <option key={u.id} value={u.id}>
                      {subjectById[u.subject_id]?.name} — {u.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-500">
                  Hours
                </label>
                <input
                  type="number"
                  min="0.5"
                  step="0.5"
                  value={hours}
                  onChange={(e) => setHours(e.target.value)}
                  className="mt-1 w-24 rounded-lg border border-slate-300 px-2 py-1.5 text-sm"
                />
              </div>
              <button className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700">
                Schedule
              </button>
            </form>
          )}
        </div>
      )}
    </div>
  );
}
