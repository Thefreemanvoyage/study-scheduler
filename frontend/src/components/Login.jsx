import { useState } from "react";
import { useAuth } from "../context/AuthContext.jsx";

// Simple username/password login with a register toggle.
export default function Login() {
  const { login, register } = useAuth();
  const [mode, setMode] = useState("login"); // "login" | "register"
  const [username, setUsername] = useState("student");
  const [password, setPassword] = useState("password123");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      if (mode === "login") await login(username, password);
      else await register(username, password);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-sm rounded-2xl bg-white p-8 shadow-lg">
        <h1 className="text-2xl font-bold text-center">📚 Study Scheduler</h1>
        <p className="mt-1 text-center text-sm text-slate-500">
          {mode === "login" ? "Sign in to continue" : "Create your account"}
        </p>

        <form onSubmit={submit} className="mt-6 space-y-4">
          <div>
            <label className="block text-sm font-medium">Username</label>
            <input
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 focus:border-brand-500 focus:outline-none"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium">Password</label>
            <input
              type="password"
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 focus:border-brand-500 focus:outline-none"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              required
            />
          </div>

          {error && (
            <p className="rounded bg-red-50 px-3 py-2 text-sm text-red-600">
              {error}
            </p>
          )}

          <button
            disabled={busy}
            className="w-full rounded-lg bg-brand-600 py-2 font-semibold text-white hover:bg-brand-700 disabled:opacity-60"
          >
            {busy ? "Please wait…" : mode === "login" ? "Login" : "Register"}
          </button>
        </form>

        <button
          onClick={() => setMode(mode === "login" ? "register" : "login")}
          className="mt-4 w-full text-center text-sm text-brand-600 hover:underline"
        >
          {mode === "login"
            ? "No account? Register"
            : "Have an account? Login"}
        </button>

        <p className="mt-4 text-center text-xs text-slate-400">
          Demo (after seeding): student / password123
        </p>
      </div>
    </div>
  );
}
