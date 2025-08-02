import "server-only";

import createClient from "openapi-fetch";
import type { paths } from "./schema";

export function createGatewayClient() {
  const headers = {
    Authorization: `Bearer ${process.env.SERVICE_TOKEN}`,
  };
  const client = createClient<paths>({
    baseUrl: process.env.GATEWAY_URL!,
    headers,
  });
  return client;
}
