import { AuthKeycloakClient } from "@/auth/keycloakclient/authkeycloakclient";
import { AuthMockClient } from "@/auth/mockclient/authmockclient";
import type { AuthClientInterface } from "@/interfaces/AuthClientInterface";

export function createAuthClient(): AuthClientInterface {
  const useMock = import.meta.env.VITE_USE_AUTH_MOCK === "true";
  return useMock ? new AuthMockClient() : new AuthKeycloakClient();
}
