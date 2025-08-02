import { db } from "@/db/client";

export async function queryGatewayToken({ userId }: { userId: string }) {
  const gatewayAccount = await db.query.account.findFirst({
    where: (account, { eq, and }) =>
      and(eq(account.userId, userId), eq(account.providerId, "gateway")),
    columns: {
      accessToken: true,
    },
  });
  return gatewayAccount!.accessToken!;
}
