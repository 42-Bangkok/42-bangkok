import { db } from "@/db/client";
import { auth } from "@/lib/auth";
import { headers } from "next/headers";
import createClient from "openapi-fetch";
import type { paths } from "./schema";

export async function createUserClient() {
  const session = await auth.api.getSession({
    headers: await headers(),
  });
  if (!session) {
    throw new Error("User is not authenticated");
  }
  const userId = session.user.id;
  const gatewayAccount = await db.query.account.findFirst({
    where: (account, { eq, and }) =>
      and(eq(account.userId, userId), eq(account.providerId, "gateway")),
    columns: {
      accessToken: true,
    },
  });
  let baseUrl = process.env.NEXT_PUBLIC_GATEWAY_URL;
  if (typeof window === "undefined") {
    baseUrl = process.env.GATEWAY_URL;
  }
  const client = createClient<paths>({
    baseUrl,
    headers: {
      Authorization: `Bearer ${gatewayAccount!.accessToken}`,
    },
  });
  return client;
}

interface IcreateUserClientByToken {
  accessToken: string;
}
export function createUserClientByToken(p: IcreateUserClientByToken) {
  let baseUrl = process.env.NEXT_PUBLIC_GATEWAY_URL;
  if (typeof window === "undefined") {
    baseUrl = process.env.GATEWAY_URL;
  }
  const client = createClient<paths>({
    baseUrl,
    headers: {
      Authorization: `Bearer ${p.accessToken}`,
    },
  });
  return client;
}
