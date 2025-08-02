import { db } from "@/db/client";
import { gatewaySignInhandler } from "@/lib/gateway-client/handlers/sign-in";
import type { CustomSessionData } from "@/types/auth";
import { betterAuth } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { createAuthMiddleware } from "better-auth/api";
import { customSession, genericOAuth } from "better-auth/plugins";
import { gatewaySignOutHandler } from "./gateway-client/handlers/sign-out";
import { queryGatewayToken } from "./gateway-client/utils/query-gateway-token";
export const auth = betterAuth({
  database: drizzleAdapter(db, {
    provider: "pg",
  }),
  socialProviders: {},
  hooks: {
    after: createAuthMiddleware(async (ctx) => {
      if (ctx.path == "/callback/:id") {
        const userId = ctx.context.newSession!.session!.userId;
        const provider = ctx.params.id;
        await gatewaySignInhandler({ userId, provider });
      }
    }),
    before: createAuthMiddleware(async (ctx) => {
      if (ctx.path == "/sign-out") {
        await gatewaySignOutHandler();
      }
    }),
  },
  plugins: [
    customSession(async ({ user, session }): Promise<CustomSessionData> => {
      const gatewayToken = await queryGatewayToken({ userId: user.id });
      return {
        user: {
          ...user,
          gatewayToken,
        },
        session,
      } as CustomSessionData;
    }),
    genericOAuth({
      config: [
        {
          providerId: "fortytwo",
          clientId: process.env.FORTYTWO_CLIENT_ID as string,
          clientSecret: process.env.FORTYTWO_CLIENT_SECRET as string,
          authorizationUrl: "https://api.intra.42.fr/oauth/authorize",
          tokenUrl: "https://api.intra.42.fr/oauth/token",
          userInfoUrl: "https://api.intra.42.fr/v2/me",
          scopes: ["public"],
        },
      ],
    }),
  ],
});
