import type { AuthClientInterface } from "@/interfaces/AuthClientInterface";
import type { TokenResponse } from "@/types/auth";
import { MOCK_CREDENTIALS, type MockCredential } from "@/data/auth";

function encodeBase64Url(obj: object): string {
  return btoa(JSON.stringify(obj))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=/g, "");
}

function createMockJwt(
  credential: MockCredential,
  expiresInSeconds: number,
): string {
  const now = Math.floor(Date.now() / 1000);
  const header = encodeBase64Url({ alg: "none", typ: "JWT" });
  const payload = encodeBase64Url({
    ...credential.user,
    exp: now + expiresInSeconds,
    iat: now,
    preferred_username: credential.username,
    realm_access: credential.realm_access,
    resource_access: credential.resource_access,
    scope: "openid profile email",
  });
  return `${header}.${payload}.mock_signature`;
}

export class AuthMockClient implements AuthClientInterface {
  async login(username: string, password: string): Promise<TokenResponse> {
    const credential = MOCK_CREDENTIALS.find(
      (c) => c.username === username && c.password === password,
    );

    if (!credential) {
      throw new Error("Credenciales inválidas");
    }

    return {
      access_token: createMockJwt(credential, 300),
      refresh_token: createMockJwt(credential, 1800),
      expires_in: 300,
      refresh_expires_in: 1800,
      token_type: "Bearer",
    };
  }

  async refresh(refreshToken: string): Promise<TokenResponse> {
    try {
      const parts = refreshToken.split(".");
      const decoded = JSON.parse(
        atob(parts[1].replace(/-/g, "+").replace(/_/g, "/")),
      );
      const username: string = decoded.preferred_username ?? "jdoe";
      const credential =
        MOCK_CREDENTIALS.find((c) => c.username === username) ??
        MOCK_CREDENTIALS[0];

      return {
        access_token: createMockJwt(credential, 300),
        refresh_token: createMockJwt(credential, 1800),
        expires_in: 300,
        refresh_expires_in: 1800,
        token_type: "Bearer",
      };
    } catch {
      throw new Error("Token de refresco inválido");
    }
  }

  async logout(_refreshToken: string): Promise<void> {
    // No network call needed for mock
  }
}
