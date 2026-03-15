import { KEYCLOAK_CONFIG } from "@/lib/keycloak";
import type { AuthClientInterface } from "@/interfaces/AuthClientInterface";
import type { TokenResponse } from "@/types/auth";

const TOKEN_ENDPOINT = `${KEYCLOAK_CONFIG.url}realms/${KEYCLOAK_CONFIG.realm}/protocol/openid-connect/token`;
const LOGOUT_ENDPOINT = `${KEYCLOAK_CONFIG.url}realms/${KEYCLOAK_CONFIG.realm}/protocol/openid-connect/logout`;

export class AuthKeycloakClient implements AuthClientInterface {
  async login(username: string, password: string): Promise<TokenResponse> {
    const response = await fetch(TOKEN_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        grant_type: "password",
        client_id: KEYCLOAK_CONFIG.clientId,
        username,
        password,
        scope: "openid profile email",
      }),
    });

    if (!response.ok) {
      throw new Error("Credenciales inválidas");
    }

    const data = await response.json();
    console.log("[AuthKeycloakClient] token response keys:", Object.keys(data));
    return data;
  }

  async refresh(refreshToken: string): Promise<TokenResponse> {
    const response = await fetch(TOKEN_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        grant_type: "refresh_token",
        client_id: KEYCLOAK_CONFIG.clientId,
        refresh_token: refreshToken,
      }),
    });
    console.log(
      "[AuthKeycloakClient] refresh response status:",
      response.status,
    );

    if (!response.ok) {
      throw new Error(`Refresh falló con status: ${response.status}`);
    }

    return response.json();
  }

  async logout(refreshToken: string): Promise<void> {
    const response = await fetch(LOGOUT_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        client_id: KEYCLOAK_CONFIG.clientId,
        refresh_token: refreshToken,
      }),
    });

    if (!response.ok) {
      console.warn(
        "[AuthKeycloakClient] Logout respondió con status:",
        response.status,
      );
    }
  }
}
