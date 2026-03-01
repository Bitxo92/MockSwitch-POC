import type { Agenda } from "@/types/agenda";

export interface AgendaClientInterface {
  getAll(): Promise<Agenda[]>;
  getById(id: number): Promise<Agenda | undefined>;
  create(data: Omit<Agenda, "id">): Promise<Agenda>;
  update(id: number, data: Omit<Agenda, "id">): Promise<Agenda | undefined>;
  delete(id: number): Promise<boolean>;
}
