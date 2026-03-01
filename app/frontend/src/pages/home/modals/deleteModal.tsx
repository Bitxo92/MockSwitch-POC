import { Trash2, X } from "lucide-react";
import { Spinner } from "@/components/ui/spinner";
import {
  AlertDialog,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";

interface DeleteModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: () => void | Promise<void>;
  title?: string;
  description?: string;
  isLoading?: boolean;
}

/*
#######################################################################################################
#                                 Initializations & State Management                                  #
#######################################################################################################
        
*/

export function DeleteModal({
  open,
  onOpenChange,
  onConfirm,
  title = "Eliminar entrada en la agenda",
  description = "¿Estás seguro de que deseas eliminar esta entrada en la agenda? Esta acción no se puede deshacer.",
  isLoading = false,
}: DeleteModalProps) {
  // Only prevent closing during deletion
  const handleOpenChange = (newOpen: boolean) => {
    // Only allow closing if not currently deleting
    if (!isLoading) {
      onOpenChange(newOpen);
    }
  };

  const handleEscapeKeyDown = (e: KeyboardEvent) => {
    // Only prevent escape if currently deleting
    if (isLoading) {
      e.preventDefault();
    }
  };

  return (
    <AlertDialog open={open} onOpenChange={handleOpenChange}>
      <AlertDialogContent onEscapeKeyDown={handleEscapeKeyDown}>
        <AlertDialogHeader>
          <AlertDialogTitle className="flex items-center gap-2">
            <Trash2 className="h-5 w-5 text-red-600" />
            {title}
          </AlertDialogTitle>
          <AlertDialogDescription>{description}</AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={isLoading}>
            <X className="h-4 w-4 mr-2" />
            Cancelar
          </AlertDialogCancel>
          <Button
            variant="destructive"
            onClick={onConfirm}
            disabled={isLoading}
            className="flex items-center gap-2"
          >
            {isLoading && <Spinner className="h-4 w-4" />}
            {isLoading ? "Eliminando..." : "Eliminar"}
          </Button>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
