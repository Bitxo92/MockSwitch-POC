import { useState, useEffect, useCallback } from "react";
import {
  X,
  Plus,
  Save,
  SquarePen,
  Trash2,
  Contact,
  Loader2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetFooter,
} from "@/components/ui/sheet";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { DeleteModal } from "@/pages/home/modals/deleteModal";

interface AgendaModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (agenda: { name: string; email: string; phone: string }) => void;
  agenda?: {
    id: number;
    name: string;
    email: string;
    phone: string;
  } | null;
  onDelete?: () => void;
  isLoading?: boolean;
  isDeleting?: boolean;
}

export function AgendaModal({
  open,
  onOpenChange,
  onSubmit,
  agenda,
  onDelete,
  isLoading = false,
  isDeleting = false,
}: AgendaModalProps) {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
  });
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);

  useEffect(() => {
    if (agenda) {
      setFormData({
        name: agenda.name,
        email: agenda.email,
        phone: agenda.phone,
      });
    } else if (open) {
      // Resetear cuando se abre para crear nuevo
      setFormData({
        name: "",
        email: "",
        phone: "",
      });
    }
  }, [agenda, open]);

  const handleInputChange = (field: string, value: string) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSubmit = useCallback(() => {
    if (!formData.name || !formData.email || !formData.phone) {
      alert("Por favor, completa todos los campos");
      return;
    }

    onSubmit({
      name: formData.name,
      email: formData.email,
      phone: formData.phone,
    });
  }, [formData, onSubmit]);

  const handleOpenChange = (newOpen: boolean) => {
    onOpenChange(newOpen);
    if (!newOpen) {
      setFormData({
        name: "",
        email: "",
        phone: "",
      });
    }
  };

  const isEditing = !!agenda;

  return (
    <>
      <Sheet open={open} onOpenChange={handleOpenChange}>
        <SheetContent
          side="right"
          className="w-[calc(100vw-5rem)] sm:max-w-[calc(100vw-5rem)] p-0 flex flex-col"
          showCloseButton={false}
        >
          {/* Loading Overlay */}
          {(isLoading || isDeleting) && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 rounded-lg">
              <div className="flex flex-col items-center gap-3">
                <Loader2 className="h-12 w-12 animate-spin text-white" />
                <p className="text-white text-lg font-semibold">
                  {isDeleting
                    ? "Eliminando..."
                    : isLoading
                      ? "Procesando..."
                      : ""}
                </p>
              </div>
            </div>
          )}
          <SheetHeader className="px-6 pt-6 pb-4 border-b">
            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gray-100">
                  {isEditing ? (
                    <SquarePen className="h-6 w-6 text-gray-600" />
                  ) : (
                    <Plus className="h-6 w-6 text-gray-600" />
                  )}
                </div>
                <div>
                  <SheetTitle className="text-2xl">
                    {isEditing ? "Editar Contacto" : "Nuevo Contacto"}
                  </SheetTitle>
                  <SheetDescription className="text-base mt-1">
                    {isEditing
                      ? "Actualiza los detalles del contacto"
                      : "Ingresa los detalles del nuevo contacto"}
                  </SheetDescription>
                </div>
              </div>
              {isEditing && onDelete && (
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setDeleteModalOpen(true)}
                  className="h-10 w-10 flex items-center justify-center hover:bg-red-50"
                >
                  <Trash2 className="h-5 w-5 text-red-600" />
                </Button>
              )}
            </div>
          </SheetHeader>

          <div className="flex-1 overflow-y-auto px-6 py-6">
            <fieldset className="bg-gray-100 border border-gray-600 rounded-lg p-4">
              <legend className="flex items-center gap-2 px-2 text-sm font-semibold">
                <Contact className="h-4 w-4" />
                Información de Contacto
              </legend>
              <div className="space-y-4 mt-3">
                <div className="space-y-2">
                  <Label htmlFor="name" className="ml-2">
                    Nombre
                  </Label>
                  <Input
                    id="name"
                    placeholder="Ej: Juan Perez"
                    value={formData.name}
                    onChange={(e) => handleInputChange("name", e.target.value)}
                    className="bg-white select-none"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email" className="ml-2">
                    Correo Electrónico
                  </Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="Ej: juan@example.com"
                    value={formData.email}
                    onChange={(e) => handleInputChange("email", e.target.value)}
                    className="bg-white select-none"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="phone" className="ml-2">
                    Teléfono
                  </Label>
                  <Input
                    id="phone"
                    placeholder="Ej: +51 984567890"
                    value={formData.phone}
                    onChange={(e) => handleInputChange("phone", e.target.value)}
                    className="bg-white select-none"
                  />
                </div>
              </div>
            </fieldset>
          </div>

          <SheetFooter className="px-6 py-4 border-t mt-auto">
            <div className="flex items-center justify-end gap-4 w-full">
              <Button
                variant="outline"
                onClick={() => handleOpenChange(false)}
                className="flex items-center gap-2 h-10 px-6 hover:cursor-pointer"
              >
                <X className="h-4 w-4" />
                Cancelar
              </Button>
              <Button
                onClick={handleSubmit}
                className="flex items-center gap-2 h-10 px-6 hover:cursor-pointer"
              >
                {isEditing ? (
                  <Save className="h-4 w-4" />
                ) : (
                  <Plus className="h-4 w-4" />
                )}
                {isEditing ? "Guardar" : "Crear"}
              </Button>
            </div>
          </SheetFooter>
        </SheetContent>
      </Sheet>

      {/* Delete Confirmation Modal */}
      {isEditing && onDelete && (
        <DeleteModal
          open={deleteModalOpen}
          onOpenChange={setDeleteModalOpen}
          onConfirm={async () => {
            await onDelete?.();
            setDeleteModalOpen(false);
          }}
          title="Eliminar contacto"
          description={`¿Estás seguro de que deseas eliminar el contacto "${agenda?.name}"? Esta acción no se puede deshacer.`}
          isLoading={isDeleting}
        />
      )}
    </>
  );
}
