import { createAuthClient } from "@/auth";
import keycloak, { KEYCLOAK_CONFIG } from "@/lib/keycloak";
import type { AuthClientInterface } from "@/interfaces/AuthClientInterface";
import type { AuthState, User } from "@/types/auth";

const STORAGE_KEY = "auth_refresh_token";

class AuthService {
  private client: AuthClientInterface;
  private state: AuthState = {
    isAuthenticated: false,
    user: null,
    isLoading: true,
    error: null,
  };
  private listeners = new Set<() => void>();
  private refreshTimerId: ReturnType<typeof setTimeout> | null = null;

  constructor(client: AuthClientInterface) {
    this.client = client;
  }

  // ── Observable ──────────────────────────────────────────────────────────────

  subscribe(listener: () => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notify(): void {
    this.state = { ...this.state };
    this.listeners.forEach((l) => l());
  }

  // ── Public API ───────────────────────────────────────────────────────────────

  getState(): AuthState {
    return this.state;
  }

  getToken(): string | null {
    return keycloak.token ?? null;
  }

  getAuthHeaders(): Record<string, string> {
    return keycloak.token ? { Authorization: `Bearer ${keycloak.token}` } : {};
  }

  // ── RBAC Helpers ─────────────────────────────────────────────────────────────

  hasRole(role: string): boolean {
    return this.state.user?.roles.includes(role) ?? false;
  }

  hasAnyRole(roles: string[]): boolean {
    return roles.some((r) => this.hasRole(r));
  }

  // ── Session Restore ─────────────────────────────────────────────────────────

  async init(): Promise<void> {
    const storedRefreshToken = localStorage.getItem(STORAGE_KEY);
    if (!storedRefreshToken) {
      this.state = { ...this.state, isLoading: false };
      this.notify();
      return;
    }

    try {
      const data = await this.client.refresh(storedRefreshToken);
      this.processTokenResponse(data);
      this.state = { ...this.state, isLoading: false };
      this.notify();
    } catch {
      localStorage.removeItem(STORAGE_KEY);
      this.state = { ...this.state, isLoading: false };
      this.notify();
    }
  }

  // ── Auth Operations ──────────────────────────────────────────────────────────

  async login(username: string, password: string): Promise<boolean> {
    this.state = { ...this.state, isLoading: true, error: null };
    this.notify();

    try {
      const data = await this.client.login(username, password);

      if (!data?.access_token) {
        throw new Error(
          "Respuesta de autenticación inválida: no se recibió access_token",
        );
      }

      this.processTokenResponse(data);
      this.state = { ...this.state, isLoading: false };
      this.notify();
      return true;
    } catch (err) {
      const error =
        err instanceof Error ? err.message : "Error de autenticación";
      this.state = {
        isAuthenticated: false,
        user: null,
        isLoading: false,
        error,
      };
      this.notify();
      return false;
    }
  }

  logout(): void {
    this.clearRefreshTimer();

    const refreshToken = keycloak.refreshToken;
    if (refreshToken) {
      this.client.logout(refreshToken).catch((err) => {
        console.warn("[AuthService] Error al invalidar sesión remota:", err);
      });
    }

    keycloak.token = undefined;
    keycloak.refreshToken = undefined;
    keycloak.tokenParsed = undefined;
    keycloak.authenticated = false;
    localStorage.removeItem(STORAGE_KEY);

    this.state = {
      isAuthenticated: false,
      user: null,
      isLoading: false,
      error: null,
    };
    this.notify();
  }

  // ── Token Processing ──────────────────────────────────────────────────────────

  private processTokenResponse(data: {
    access_token: string;
    refresh_token: string;
    expires_in: number;
  }): void {
    // Sync keycloak-js adapter
    keycloak.token = data.access_token;
    keycloak.refreshToken = data.refresh_token;
    keycloak.authenticated = true;

    // Decode JWT
    const tokenParts = data.access_token.split(".");
    if (tokenParts.length === 3) {
      keycloak.tokenParsed = JSON.parse(
        atob(tokenParts[1].replace(/-/g, "+").replace(/_/g, "/")),
      );
    }

    // Persist refresh token for session restore
    localStorage.setItem(STORAGE_KEY, data.refresh_token);

    // Update auth state
    const user = this.formatUser(keycloak.tokenParsed);
    this.state = { ...this.state, isAuthenticated: true, user, error: null };

    // Schedule automatic refresh
    this.scheduleRefresh(data.expires_in);
  }

  // ── Token Refresh ─────────────────────────────────────────────────────────────

  private scheduleRefresh(expiresInS: number): void {
    this.clearRefreshTimer();
    const delayMs = Math.max((expiresInS - 30) * 1000, 0);
    this.refreshTimerId = setTimeout(() => this.doRefresh(), delayMs);
  }

  private clearRefreshTimer(): void {
    if (this.refreshTimerId !== null) {
      clearTimeout(this.refreshTimerId);
      this.refreshTimerId = null;
    }
  }

  private async doRefresh(): Promise<void> {
    if (!keycloak.refreshToken) {
      this.logout();
      return;
    }

    try {
      const data = await this.client.refresh(keycloak.refreshToken);
      this.processTokenResponse(data);
      this.notify();
    } catch {
      this.logout();
    }
  }

  // ── User Mapping ──────────────────────────────────────────────────────────────

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private formatUser(tokenParsed: any): User | null {
    if (!tokenParsed) return null;

    return {
      id: tokenParsed.sub ?? "",
      username: tokenParsed.preferred_username ?? "",
      email: tokenParsed.email ?? "",
      name: tokenParsed.name ?? "",
      roles:
        tokenParsed.resource_access?.[KEYCLOAK_CONFIG.clientId]?.roles ?? [],
      password_expiration: null,
    };
  }
}

export const authService = new AuthService(createAuthClient());

// Restore session on app start
authService.init();
