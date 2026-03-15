import {
  AlertCircle,
  BookUser,
  Loader2,
  LogOut,
  Plus,
  Search,
  SquarePen,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/auth/useAuth";
import { useState, useMemo } from "react";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";
import { AgendaModal } from "@/pages/home/modals/agendaModal";
import {
  useAgenda,
  useCreateAgenda,
  useUpdateAgenda,
  useDeleteAgenda,
} from "@/hooks/api/useAgenda";
import type { Agenda } from "@/types/agenda";
import { useUser } from "@/hooks/auth/useAuth";

export default function HomePage() {
  const { logout } = useAuth();
  const { data: agendas = [], isPending: isLoadingAgendas } = useAgenda();
  const { user } = useUser();

  // Store mutations as objects (not destructured)
  const createMutation = useCreateAgenda();
  const updateMutation = useUpdateAgenda();
  const deleteMutation = useDeleteAgenda();

  const ITEMS_PER_PAGE = 8;
  const [searchTerm, setSearchTerm] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedAgenda, setSelectedAgenda] = useState<Agenda | null>(null);
  const [modalOpen, setModalOpen] = useState(false);

  const filteredAgendas = useMemo(() => {
    const term = searchTerm.toLowerCase();
    return agendas.filter(
      (agenda: Agenda) =>
        agenda.name.toLowerCase().includes(term) ||
        agenda.email.toLowerCase().includes(term) ||
        agenda.phone.includes(term),
    );
  }, [agendas, searchTerm]);

  const totalPages = Math.ceil(filteredAgendas.length / ITEMS_PER_PAGE);
  const paginatedAgendas = useMemo(() => {
    const startIdx = (currentPage - 1) * ITEMS_PER_PAGE;
    return filteredAgendas.slice(startIdx, startIdx + ITEMS_PER_PAGE);
  }, [filteredAgendas, currentPage]);

  const handleNewClick = () => {
    setSelectedAgenda(null);
    setModalOpen(true);
  };

  const handleEditClick = (agenda: Agenda) => {
    setSelectedAgenda(agenda);
    setModalOpen(true);
  };

  const handleModalSubmit = async (data: Omit<Agenda, "id">) => {
    try {
      if (selectedAgenda) {
        // Update existing agenda
        await updateMutation.mutateAsync({
          id: selectedAgenda.id,
          data,
        });
      } else {
        // Create new agenda
        await createMutation.mutateAsync(data);
      }
      setSelectedAgenda(null);
      setModalOpen(false);
    } catch (err) {
      console.error("Error al procesar contacto:", err);
    }
  };

  const handleDelete = async () => {
    if (selectedAgenda) {
      try {
        await deleteMutation.mutateAsync(selectedAgenda.id);
        setSelectedAgenda(null);
        setModalOpen(false);
      } catch (err) {
        console.error("Error al eliminar contacto:", err);
      }
    }
  };

  return (
    <div className="flex min-h-screen">
      <main className="flex-1 px-2 md:py-2">
        {/**Header Container */}
        <div className="grid grid-cols-2 gap-6 mb-10">
          {" "}
          <div className="w-[80%]">
            {/**Title Section */}
            <div className="flex items-center gap-3 mb--2">
              <BookUser className="size-8 text-primary" />
              <h1 className="text-4xl font-bold">Agenda</h1>
            </div>
            <p className="text-lg text-left text-muted-foreground mb-2">
              Gestiona tus contactos de manera eficiente
            </p>
          </div>
          {/**Logout  button*/}
          <div className="flex flex-col justify-end items-center gap-2">
            <div className="flex justify-center place-items-center mx-auto ">
              <span>{user?.name}</span>
            </div>
            <Button
              className="w-[20%] bg-red-600 hover:bg-red-700 hover:cursor-pointer"
              onClick={logout}
            >
              <div className="flex items-center gap-2">
                <LogOut className="h-4 w-4" />
                Logout
              </div>
            </Button>
          </div>
        </div>
        {/* Search and Filter Section */}
        <div className="flex gap-4 mb-8 w-full">
          {/* Search Bar */}
          <div className="relative w-[90%]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
            <Input
              placeholder="Buscar por nombre, correo o teléfono"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4"
              disabled={false}
            />
          </div>

          {/* New Button Row */}
          <div className="flex items-center justify-end w-[10%]">
            <Button
              onClick={handleNewClick}
              className="flex items-center w-full gap-2 hover:cursor-pointer"
              disabled={
                isLoadingAgendas ||
                createMutation.isPending ||
                updateMutation.isPending ||
                deleteMutation.isPending
              }
            >
              <div className="flex items-center gap-2">
                <Plus className="h-4 w-4" />
                Nuevo
              </div>
            </Button>
          </div>
        </div>

        {/**Contacts Table */}
        <div className="rounded-lg border overflow-hidden">
          <div>
            <Table>
              <TableHeader>
                <TableRow className="bg-black hover:bg-black">
                  <TableHead className="text-center text-background">
                    Nombre
                  </TableHead>
                  <TableHead className="text-center text-background">
                    Correo
                  </TableHead>
                  <TableHead className="text-center text-background">
                    Teléfono
                  </TableHead>
                  <TableHead className="text-center text-background">
                    Editar
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoadingAgendas ? (
                  <TableRow>
                    <TableCell
                      colSpan={4}
                      className="text-center text-muted-foreground py-8"
                    >
                      <div className="flex flex-col items-center justify-center gap-2 m-10">
                        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground/60" />
                        <span className="pt-2">Cargando contactos...</span>
                      </div>
                    </TableCell>
                  </TableRow>
                ) : paginatedAgendas.length === 0 ? (
                  <TableRow>
                    <TableCell
                      colSpan={4}
                      className="text-center text-muted-foreground py-8"
                    >
                      <div className="flex flex-col items-center justify-center gap-2 m-10">
                        <AlertCircle className="h-8 w-8 text-muted-foreground/60" />
                        <span className="pt-2">Sin datos disponibles</span>
                      </div>
                    </TableCell>
                  </TableRow>
                ) : (
                  paginatedAgendas.map((agenda) => (
                    <TableRow key={agenda.id}>
                      <TableCell className="text-center">
                        {agenda.name}
                      </TableCell>
                      <TableCell className="text-center">
                        {agenda.email}
                      </TableCell>
                      <TableCell className="text-center">
                        {agenda.phone}
                      </TableCell>
                      <TableCell className="text-center">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleEditClick(agenda)}
                          disabled={
                            createMutation.isPending ||
                            updateMutation.isPending ||
                            deleteMutation.isPending
                          }
                          className="flex items-center gap-2 mx-auto hover:cursor-pointer"
                        >
                          <SquarePen className="h-4 w-4" />
                          Editar
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="border-t px-4 py-3">
              <Pagination>
                <PaginationContent>
                  <PaginationItem>
                    <PaginationPrevious
                      onClick={() =>
                        setCurrentPage((prev) => Math.max(1, prev - 1))
                      }
                      className={
                        currentPage === 1
                          ? "pointer-events-none opacity-50"
                          : "cursor-pointer"
                      }
                    />
                  </PaginationItem>

                  {Array.from({ length: totalPages }, (_, i) => i + 1).map(
                    (page) => (
                      <PaginationItem key={page}>
                        <PaginationLink
                          onClick={() => setCurrentPage(page)}
                          isActive={page === currentPage}
                          className="cursor-pointer"
                        >
                          {page}
                        </PaginationLink>
                      </PaginationItem>
                    ),
                  )}

                  <PaginationItem>
                    <PaginationNext
                      onClick={() =>
                        setCurrentPage((prev) => Math.min(totalPages, prev + 1))
                      }
                      className={
                        currentPage === totalPages
                          ? "pointer-events-none opacity-50"
                          : "cursor-pointer"
                      }
                    />
                  </PaginationItem>
                </PaginationContent>
              </Pagination>
            </div>
          )}
        </div>

        {/* Agenda Modal */}
        <AgendaModal
          open={modalOpen}
          onOpenChange={setModalOpen}
          onSubmit={handleModalSubmit}
          agenda={selectedAgenda}
          onDelete={selectedAgenda ? handleDelete : undefined}
          isLoading={createMutation.isPending || updateMutation.isPending}
          isDeleting={deleteMutation.isPending}
        />
      </main>
    </div>
  );
}
