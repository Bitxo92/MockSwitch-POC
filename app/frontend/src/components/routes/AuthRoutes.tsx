import { Navigate } from "react-router-dom";
import { useAuth } from "@/hooks/auth/useAuth";

/**
 * Envuelve rutas que requieren autenticación.
 * Redirige a /login si el usuario no está autenticado.
 * Espera a que termine la restauración de sesión antes de decidir.
 */
export function ProtectedRoute({ element }: { element: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return null;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return element;
}

/**
 * Envuelve la ruta de login.
 * Redirige a / si el usuario ya está autenticado.
 * Espera a que termine la restauración de sesión antes de decidir.
 */
export function LoginRoute({ element }: { element: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return null;
  }

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return element;
}
