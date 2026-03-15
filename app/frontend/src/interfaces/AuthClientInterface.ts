import type { TokenResponse } from "@/types/auth";

export interface AuthClientInterface {
  login(username: string, password: string): Promise<TokenResponse>;
  refresh(refreshToken: string): Promise<TokenResponse>;
  logout(refreshToken: string): Promise<void>;
}
