import { and, eq } from "drizzle-orm";
import { nanoid } from "nanoid";
import { redirect } from "next/navigation";

import { db } from "@/db/client";
import { account } from "@/db/schema";
import { createGatewayClient } from "@/lib/gateway-client/clients.server";
import { createUserClientByToken } from "../clients";

export interface IGatewayLoginHandler {
  userId: string;
  provider: string;
}

/**
 * Handles gateway login process for a user with an existing provider account.
 *
 * This function performs the following operations:
 * 1. Retrieves the user's provider account from the database
 * 2. Authenticates with the gateway service using the provider's access token
 * 3. Fetches user information from the gateway
 * 4. Updates existing gateway account credentials or creates a new gateway account record
 *
 * @param p - Gateway login handler parameters
 * @param p.userId - The ID of the user performing the login
 * @param p.provider - The provider identifier for the existing account
 *
 * @throws {Error} When gateway login fails or user data cannot be fetched
 *
 * @returns {Promise<void>} Resolves when the gateway account is successfully created or updated
 */
export async function gatewaySignInhandler(p: IGatewayLoginHandler) {
  const { userId, provider } = p;
  const providerAccount = await db.query.account.findFirst({
    where: (account, { eq, and }) =>
      and(eq(account.userId, userId!), eq(account.providerId, provider!)),
  });
  const gatewayServiceClient = createGatewayClient();
  const { data: gatewayLogin, error: gatewayLoginError } =
    await gatewayServiceClient.POST(
      "/api/account/auths/login/",
      // @ts-expect-error these are ok
      { body: { provider, access_token: providerAccount.accessToken } }
    );
  if (gatewayLoginError) {
    console.error("Error logging in to gateway:", gatewayLoginError);
    throw new Error("Failed to log in to gateway");
  }
  const gatewayUserClient = createUserClientByToken({
    accessToken: gatewayLogin.access_token,
  });
  // throw if the response is not ok
  const { data: gatewayMe, error: meError } = await gatewayUserClient.GET(
    "/api/account/users/me/"
  );
  if (meError) {
    console.error("Error fetching user data from gateway:", meError);
    // Redirect to logout page to force logout and redirect to login
    redirect("/auth/logout");
  }
  if (
    await db.query.account.findFirst({
      where: (account, { eq, and }) =>
        and(
          eq(account.userId, userId!),
          eq(account.accountId, gatewayMe.user.id!),
          eq(account.providerId, "gateway")
        ),
    })
  ) {
    await db
      .update(account)
      .set({
        accessToken: gatewayLogin.access_token,
        refreshToken: gatewayLogin.refresh_token,
        accessTokenExpiresAt: new Date(
          gatewayLogin.expires_in * 1000 + Date.now()
        ),
        refreshTokenExpiresAt: new Date(
          gatewayLogin.refresh_token_expires_in * 1000 + Date.now()
        ),
        updatedAt: new Date(),
      })
      .where(
        and(
          eq(account.userId, userId!),
          eq(account.accountId, gatewayMe.user.id!),
          eq(account.providerId, "gateway")
        )
      );
    return;
  }
  await db.insert(account).values({
    id: nanoid(),
    userId: userId!,
    accountId: gatewayMe.user.id!,
    providerId: "gateway",
    accessToken: gatewayLogin.access_token,
    accessTokenExpiresAt: new Date(gatewayLogin.expires_in * 1000 + Date.now()),
    refreshTokenExpiresAt: new Date(
      gatewayLogin.refresh_token_expires_in * 1000 + Date.now()
    ),
    refreshToken: gatewayLogin.refresh_token,
    createdAt: new Date(),
    updatedAt: new Date(),
  });
}
