import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { agendaClient } from "@/api/index";
import { type Agenda } from "@/types/agenda";

export const useAgenda = () => {
  return useQuery({
    queryKey: ["agenda"],
    queryFn: () => agendaClient.getAll(),
    staleTime: 0,
    gcTime: 0,
    refetchOnMount: true,
  });
};

export const useAgendaById = (id: number) => {
  return useQuery({
    queryKey: ["agenda", id],
    queryFn: () => agendaClient.getById(id!),
    enabled: id !== null,
  });
};

export const useCreateAgenda = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Omit<Agenda, "id">) => agendaClient.create(data),
    onSuccess: (newAgenda) => {
      queryClient.setQueryData(["agenda"], (oldData: Agenda[] | undefined) => {
        if (!oldData) return [newAgenda];
        return [...oldData, newAgenda];
      });
      queryClient.invalidateQueries({ queryKey: ["agenda"] });
    },
  });
};

export const useUpdateAgenda = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Omit<Agenda, "id"> }) =>
      agendaClient.update(id, data),
    onSuccess: (updatedAgenda) => {
      if (!updatedAgenda) return;
      queryClient.setQueryData(["agenda"], (oldData: Agenda[] | undefined) => {
        if (!oldData) return [updatedAgenda];
        return oldData.map((agenda) =>
          agenda.id === updatedAgenda.id ? updatedAgenda : agenda,
        );
      });
      queryClient.invalidateQueries({ queryKey: ["agenda"] });
    },
  });
};

export const useDeleteAgenda = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => agendaClient.delete(id),
    onSuccess: (success, id) => {
      if (!success) return;
      queryClient.setQueryData(["agenda"], (oldData: Agenda[] | undefined) => {
        if (!oldData) return oldData;
        return oldData.filter((agenda) => agenda.id !== id);
      });
      queryClient.invalidateQueries({ queryKey: ["agenda"] });
    },
  });
};
