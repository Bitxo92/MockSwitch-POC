import { useSyncExternalStore, useCallback } from "react";
import { authService } from "@/services/AuthService";

export function useAuth() {
  const state = useSyncExternalStore(
    (listener) => authService.subscribe(listener),
    () => authService.getState(),
  );

  const login = useCallback(
    (username: string, password: string) =>
      authService.login(username, password),
    [],
  );
  const logout = useCallback(() => authService.logout(), []);

  return {
    ...state,
    login,
    logout,
  };
}

export function useUser() {
  const state = useSyncExternalStore(
    (listener) => authService.subscribe(listener),
    () => authService.getState(),
  );

  return {
    user: state.user,
    isAuthenticated: state.isAuthenticated,
    token: authService.getToken(),
    hasRole: (role: string) => authService.hasRole(role),
    hasAnyRole: (roles: string[]) => authService.hasAnyRole(roles),
    getAuthHeaders: () => authService.getAuthHeaders(),
  };
}


