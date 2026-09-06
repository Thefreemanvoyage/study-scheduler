import { createContext, useContext, useEffect, useState } from "react";
import { api } from "../api";

const AuthContext = createContext(null);

// Provides the logged-in username + token and login/register/logout actions.
export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("token"));
  const [username, setUsername] = useState(
    () => localStorage.getItem("username") || ""
  );

  useEffect(() => {
    if (token) localStorage.setItem("token", token);
    else localStorage.removeItem("token");
  }, [token]);

  const persist = (data) => {
    setToken(data.access_token);
    setUsername(data.username);
    localStorage.setItem("username", data.username);
  };

  const login = async (u, p) => persist(await api.login(u, p));
  const register = async (u, p) => persist(await api.register(u, p));

  const logout = () => {
    setToken(null);
    setUsername("");
    localStorage.removeItem("username");
  };

  return (
    <AuthContext.Provider
      value={{ token, username, isAuthed: !!token, login, register, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
