import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

const links = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/calendar", label: "Calendar" },
  { to: "/workload", label: "Workload" },
  { to: "/reminders", label: "Reminders" },
];

// App chrome: top nav bar + routed page content.
export default function Layout() {
  const { username, logout } = useAuth();

  return (
    <div className="min-h-full">
      <header className="bg-brand-600 text-white shadow">
        <div className="mx-auto max-w-6xl px-4 py-3 flex items-center gap-6">
          <span className="text-lg font-bold">📚 Study Scheduler</span>
          <nav className="flex gap-1">
            {links.map((l) => (
              <NavLink
                key={l.to}
                to={l.to}
                end={l.end}
                className={({ isActive }) =>
                  `rounded px-3 py-1.5 text-sm font-medium transition ${
                    isActive ? "bg-white/20" : "hover:bg-white/10"
                  }`
                }
              >
                {l.label}
              </NavLink>
            ))}
          </nav>
          <div className="ml-auto flex items-center gap-3 text-sm">
            <span className="opacity-90">Hi, {username}</span>
            <button
              onClick={logout}
              className="rounded bg-white/15 px-3 py-1.5 font-medium hover:bg-white/25"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-6">
        <Outlet />
      </main>
    </div>
  );
}
