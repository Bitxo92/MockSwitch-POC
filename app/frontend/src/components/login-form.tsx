import { cn } from "@/lib/utils";
import logo from "@/assets/tai_logo.png";
import errorIcon from "@/assets/tai-loginerror-logo.png";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Field, FieldGroup, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { Eye, EyeOff, User, Lock, LogIn } from "lucide-react";
import { useEffect, useState } from "react";
import { useAuth } from "@/hooks/auth/useAuth";
import { useNavigate } from "react-router-dom";
import taiLogo from "@/assets/tai-logo.png";
import { Spinner } from "@/components/ui/spinner";
import Spacer from "@/components/ui/spacer";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
//ZOD & RHF Imports
import { zodResolver } from "@hookform/resolvers/zod";
import { Controller, useForm } from "react-hook-form";
import { z } from "zod";

// ─── Validation Schema ───────────────────────────────────────────────────────
const LoginSchema = z.object({
  username: z.string().min(1, "campo requerido"),
  password: z.string().min(1, "campo requerido"),
});

type LoginFormData = z.infer<typeof LoginSchema>;

export function LoginForm({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const { login, isLoading, error } = useAuth();
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [errorDialogOpen, setErrorDialogOpen] = useState(false);

  const form = useForm<LoginFormData>({
    resolver: zodResolver(LoginSchema),
    defaultValues: {
      username: "",
      password: "",
    },
  });

  const handleSubmit = async (data: LoginFormData) => {
    const success = await login(data.username, data.password);
    if (success) {
      navigate("/");
    }
  };

  useEffect(() => {
    if (error) {
      setErrorDialogOpen(true);
    }
  }, [error]);

  return (
    <div
      className={cn("flex flex-col gap-6 w-[60%] min-w-[30%] ", className)}
      {...props}
    >
      <Card className="overflow-hidden p-0 w-full border-[#f03e22] border-5 shadow-lg">
        <CardContent className="grid p-0 grid-cols-1 [@media(min-width:960px)]:grid-cols-2 w-full">
          <form
            className="p-4 sm:p-6 md:p-8 w-full"
            onSubmit={form.handleSubmit(handleSubmit)}
          >
            <FieldGroup>
              <div className="flex flex-col items-center gap-2 text-center mb-4">
                <h1 className="text-2xl sm:text-3xl text-primary font-bold">
                  Bienvenido
                </h1>
                <p className="text-muted-foreground text-balance text-sm sm:text-base">
                  Inicia sesión en tu cuenta
                </p>
              </div>
              <Controller
                name="username"
                control={form.control}
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel
                      htmlFor="username"
                      className="inline-flex items-center gap-2 pl-3 text-sm"
                    >
                      <User className="h-4 w-4" />
                      Usuario
                    </FieldLabel>
                    <div className="relative">
                      <Input
                        {...field}
                        id="username"
                        className="truncate"
                        type="text"
                        aria-invalid={fieldState.invalid}
                        placeholder="introduce tu nombre de usuario"
                        autoComplete="off"
                      />
                      {fieldState.error && (
                        <p className="text-sm text-red-500 text-left ml-2 mt-2">
                          {fieldState.error.message}
                        </p>
                      )}
                    </div>
                  </Field>
                )}
              />
              <Controller
                name="password"
                control={form.control}
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
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
                        {...field}
                        id="password"
                        className="truncate"
                        aria-invalid={fieldState.invalid}
                        placeholder="introduce tu contraseña"
                        type={showPassword ? "text" : "password"}
                        autoComplete="off"
                      />
                      {fieldState.error && (
                        <p className="text-sm text-red-500 text-left ml-2 mt-2">
                          {fieldState.error.message}
                        </p>
                      )}

                      {!fieldState.error && (
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
                      )}
                    </div>
                  </Field>
                )}
              />
              <Spacer size={14} />
              <Field>
                <Button
                  type="submit"
                  className="bg-[#f03e22] w-full cursor-pointer py-6 text-md"
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
                  className="h-3 md:h-5 object-contain"
                />
              </div>
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
      {/* Error Dialog */}
      <Dialog open={errorDialogOpen} onOpenChange={setErrorDialogOpen}>
        <DialogContent className="bg-linear-to-b from-red-200 to-red-50 max-w-sm md:max-w-lg p-0 overflow-hidden border-red-500 border-5 [&>button]:hidden">
          <div className="grid grid-cols-1 md:grid-cols-2">
            {/* Image section */}
            <div className=" flex items-center justify-center p-2 md:p-6">
              <img
                src={errorIcon}
                alt="Login error"
                className="max-h-20  md:max-h-40 object-contain"
              />
            </div>

            {/* Text section */}
            <div className="p-4 md:p-6 flex flex-col justify-center gap-3 md:gap-4">
              <DialogHeader>
                <DialogTitle className="text-center">
                  Error al iniciar sesión
                </DialogTitle>
                <DialogDescription className="text-red-500 text-center">
                  {error}
                </DialogDescription>
              </DialogHeader>

              <Button
                className="w-40 md:w-full mx-auto hover:cursor-pointer hover:bg-white hover:text-black hover:border-black hover:border-3"
                onClick={() => setErrorDialogOpen(false)}
              >
                Cerrar
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
