import { AgendaHttpClient } from "@/api/agenda/httpclient/agendaHttpClient";
import { AgendaMockClient } from "@/api/agenda/mockclient/agendaMockClient";
import { mockswitch_config } from "@/api/mockswitch_config";

const USE_MOCK = mockswitch_config;

export const agendaClient = USE_MOCK
  ? new AgendaMockClient()
  : new AgendaHttpClient();
