import { AgendaHttpClient } from "@/api/httpclient/agendaHttpClient";
import { AgendaMockClient } from "@/api/mockclient/agendaMockClient";

const USE_MOCK = true;

export const agendaClient = USE_MOCK
  ? new AgendaMockClient()
  : new AgendaHttpClient();
