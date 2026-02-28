import { cn } from "@/lib/utils";
import logo from "@/assets/tai_logo.png";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Field, FieldGroup, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { Eye, EyeOff, User, Lock, LogIn } from "lucide-react";
import { useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import taiLogo from "@/assets/tai-logo.png";
import { Spinner } from "@/components/ui/spinner";
import Spacer from "@/components/ui/spacer";

export function LoginForm({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const { login, isLoading, error } = useAuth();
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const success = await login(username, password);
    if (success) {
      navigate("/");
    }
  };

  return (
    <div
      className={cn("flex flex-col gap-6 w-[60%] min-w-[30%] ", className)}
      {...props}
    >
      <Card className="overflow-hidden p-0 w-full">
        <CardContent className="grid p-0 grid-cols-1 [@media(min-width:960px)]:grid-cols-2 w-full">
          <form className="p-4 sm:p-6 md:p-8 w-full" onSubmit={handleSubmit}>
            <FieldGroup>
              <div className="flex flex-col items-center gap-2 text-center mb-4">
                <h1 className="text-2xl sm:text-3xl text-primary font-bold">
                  Bienvenido
                </h1>
                <p className="text-muted-foreground text-balance text-sm sm:text-base">
                  Inicia sesión en tu cuenta
                </p>
              </div>
              <Field>
                <FieldLabel
                  htmlFor="username"
                  className="inline-flex items-center gap-2 pl-3 text-sm"
                >
                  <User className="h-4 w-4" />
                  Usuario
                </FieldLabel>
                <Input
                  id="username"
                  type="text"
                  placeholder="introduce tu nombre de usuario"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />
              </Field>
              <Field>
                <div className="flex items-center">
                  <FieldLabel
                    htmlFor="password"
                    className="inline-flex items-center gap-2 pl-3 text-sm"
                  >
                    <Lock className="h-4 w-4" />
                    Contraseña
                  </FieldLabel>
                </div>
                <div className="relative">
                  <Input
                    id="password"
                    placeholder="introduce tu contraseña"
                    type={showPassword ? "text" : "password"}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground cursor-pointer"
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </Field>
              <Spacer size={14} />
              <Field>
                <Button
                  type="submit"
                  className="w-full cursor-pointer py-6 text-md"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <Spinner className="h-6 w-6 mr-2" />
                  ) : (
                    <LogIn className="h-6 w-6 mr-2" />
                  )}
                  {isLoading ? "Iniciando sesión..." : "Login"}
                </Button>
              </Field>

              <div className="flex flex-col items-center gap-2">
                <p className="text-xs text-muted-foreground">developed by</p>
                <img
                  src={taiLogo}
                  alt="TAI Logo"
                  className="h-5 object-contain"
                />
              </div>
              {error && (
                <div className="text-sm text-red-500 text-center">{error}</div>
              )}
            </FieldGroup>
          </form>
          <div className="bg-gray-100 relative hidden [@media(min-width:960px)]:flex flex-col items-center justify-center h-full min-h-96 gap-4 p-6">
            <img
              src={logo}
              alt="Logo"
              className="max-h-80 max-w-full object-contain"
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
