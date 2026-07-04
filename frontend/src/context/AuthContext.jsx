import { useCallback, useEffect, useMemo, useState } from "react";

import { getMe, login as loginRequest, logout as logoutRequest } from "../api/authApi";
import { tokenStore } from "../api/axiosInstance";
import { AuthContext } from "./authContext";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const clearSession = useCallback(() => {
    tokenStore.clearTokens();
    setUser(null);
  }, []);

  const restoreSession = useCallback(async () => {
    if (!tokenStore.getAccessToken()) {
      setIsLoading(false);
      return;
    }

    try {
      const currentUser = await getMe();
      setUser(currentUser);
    } catch {
      clearSession();
    } finally {
      setIsLoading(false);
    }
  }, [clearSession]);

  useEffect(() => {
    restoreSession();
  }, [restoreSession]);

  useEffect(() => {
    window.addEventListener("hrms:auth-expired", clearSession);
    return () => window.removeEventListener("hrms:auth-expired", clearSession);
  }, [clearSession]);

  const login = useCallback(async (email, password) => {
    const tokens = await loginRequest(email, password);
    tokenStore.setTokens(tokens);

    const currentUser = await getMe();
    setUser(currentUser);
    return currentUser;
  }, []);

  const logout = useCallback(async () => {
    try {
      if (tokenStore.getAccessToken()) {
        await logoutRequest();
      }
    } finally {
      clearSession();
    }
  }, [clearSession]);

  const value = useMemo(
    () => ({
      user,
      role: user?.role,
      isAuthenticated: Boolean(user),
      isLoading,
      login,
      logout,
      restoreSession,
    }),
    [isLoading, login, logout, restoreSession, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
