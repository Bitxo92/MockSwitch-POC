import type { AgendaClientInterface } from "@/interfaces/AgendaClientInterface";
import type { Agenda } from "@/types/agenda";

export class AgendaHttpClient implements AgendaClientInterface {
  getAll(): Promise<Agenda[]> {
    throw new Error("Method not implemented.");
  }
  getById(id: number): Promise<Agenda | undefined> {
    throw new Error("Method not implemented.");
  }
  create(data: Omit<Agenda, "id">): Promise<Agenda> {
    throw new Error("Method not implemented.");
  }
  update(id: number, data: Omit<Agenda, "id">): Promise<Agenda | undefined> {
    throw new Error("Method not implemented.");
  }
  delete(id: number): Promise<boolean> {
    throw new Error("Method not implemented.");
  }
}
