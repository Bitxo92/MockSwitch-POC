import type { AgendaClientInterface } from "@/interfaces/AgendaClientInterface";
import type { Agenda } from "@/types/agenda";

const apiBase = "/api/public";

export class AgendaHttpClient implements AgendaClientInterface {
  async getAll(): Promise<Agenda[]> {
    const response = await fetch(`${apiBase}/agenda`);
    if (!response.ok) {
      throw new Error("Failed to fetch agenda items");
    }
    const result = await response.json();

    return result.data;
  }
  async getById(id: number): Promise<Agenda | undefined> {
    const response = await fetch(`${apiBase}/agenda/${id}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch agenda item with id ${id}`);
    }
    const result = await response.json();
    return result.data;
  }
  async create(data: Omit<Agenda, "id">): Promise<Agenda> {
    const response = await fetch(`${apiBase}/agenda`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error("Error al crear agenda");
    const result = await response.json();
    return result.data;
  }
  async update(
    id: number,
    data: Omit<Agenda, "id">,
  ): Promise<Agenda | undefined> {
    const response = await fetch(`${apiBase}/agenda/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error(`Error al actualizar agenda ${id}`);
    const result = await response.json();
    return result.data;
  }
  async delete(id: number): Promise<boolean> {
    const response = await fetch(`${apiBase}/agenda/${id}`, {
      method: "DELETE",
    });
    if (!response.ok) throw new Error(`Error al eliminar agenda ${id}`);
    return true;
  }
}
