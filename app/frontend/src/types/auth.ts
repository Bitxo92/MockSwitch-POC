export interface User {
  id: string;
  username: string;
  email: string;
  name: string;
  roles: string[];
  password_expiration: number | null;
  rol?: string;
  perm?: string[];
}

export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  isLoading: boolean;
  error: string | null;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  refresh_expires_in: number;
  token_type: string;
}

/** Keycloak Groups Interface */
export interface ResourceRoles {
  roles: string[];
}

/** RLS Interface*/
export interface RlsFilter {
  [field: string]: string[];
}

/** Keycloak-token Payload Interface */
export interface KeycloakAccessTokenPayload {
  sub: string;
  exp: number;
  iat: number;
  jti: string;
  iss: string;
  aud: string[];
  typ: string;
  azp: string;
  sid: string;
  acr: string;
  "allowed-origins": string[];
  realm_access: {
    roles: string[];
  };
  resource_access?: {
    app?: ResourceRoles;
    api?: ResourceRoles;
    account?: ResourceRoles;
    [clientId: string]: ResourceRoles | undefined;
  };
  scope: string;
  email_verified: boolean;
  name: string;
  rls?: Record<string, RlsFilter>;
  preferred_username: string;
  given_name: string;
  family_name: string;
  email: string;
}
