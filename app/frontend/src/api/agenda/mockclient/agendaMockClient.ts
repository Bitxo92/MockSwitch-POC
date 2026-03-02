import { type Agenda } from "@/types/agenda";
import { agendaData } from "@/data/agenda";
import type { AgendaClientInterface } from "@/interfaces/AgendaClientInterface";

export class AgendaMockClient implements AgendaClientInterface {
  private delay = (ms = 2000) =>
    new Promise((resolve) => setTimeout(resolve, ms));

  async getAll(): Promise<Agenda[]> {
    await this.delay();
    return [...agendaData];
  }

  async getById(id: number): Promise<Agenda | undefined> {
    await this.delay();
    return agendaData.find((agenda) => agenda.id === id);
  }

  async create(agenda: Omit<Agenda, "id">): Promise<Agenda> {
    await this.delay();
    const maxId = agendaData.reduce((max, a) => Math.max(max, a.id), 0);
    const newAgenda: Agenda = {
      id: maxId + 1,
      ...agenda,
    };
    agendaData.push(newAgenda);
    return newAgenda;
  }

  async update(
    id: number,
    updatedAgenda: Omit<Agenda, "id">,
  ): Promise<Agenda | undefined> {
    await this.delay();
    const index = agendaData.findIndex((agenda) => agenda.id === id);
    if (index === -1) return undefined;
    const updated = { id, ...updatedAgenda };
    agendaData[index] = updated;
    return updated;
  }

  async delete(id: number): Promise<boolean> {
    await this.delay();
    const index = agendaData.findIndex((agenda) => agenda.id === id);
    if (index === -1) return false;
    agendaData.splice(index, 1);
    return true;
  }
}
