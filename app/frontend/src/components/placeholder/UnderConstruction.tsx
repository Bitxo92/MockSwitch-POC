import { Construction } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";

export default function UnderConstruction() {
  const { logout } = useAuth();

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="flex flex-col items-center justify-center text-center py-12">
        <h1 className="text-2xl font-bold mb-4">Página en construcción</h1>
        <Construction className="h-20 w-20 text-amber-400" aria-hidden="true" />
        <p className="mt-3 text-sm text-muted-foreground">Volver más tarde</p>
        <Button onClick={logout} className="mt-6">
          Cerrar sesión
        </Button>
      </div>
    </div>
  );
}
