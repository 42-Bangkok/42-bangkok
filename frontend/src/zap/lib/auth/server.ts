import { betterAuth } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { createAuthMiddleware } from "better-auth/api";
import {
  admin,
  anonymous,
  organization,
  twoFactor,
  username,
} from "better-auth/plugins";
import { passkey } from "better-auth/plugins/passkey";

import { SETTINGS } from "@/data/settings";
import { db } from "@/db";
import { createUserClient } from "@/openapi/clients";
import {
  sendForgotPasswordMail,
  sendVerificationEmail,
} from "@/zap/actions/emails.action";
import { canSendEmail, updateLastEmailSent } from "@/zap/lib/resend/rate-limit";

import { gatewayLoginHandler } from "./utils";

export const auth = betterAuth({
  appName: "Zap.ts",
  database: drizzleAdapter(db, { provider: "pg" }),
  emailAndPassword: {
    enabled: true,
    minPasswordLength: SETTINGS.AUTH.MINIMUM_PASSWORD_LENGTH,
    maxPasswordLength: SETTINGS.AUTH.MAXIMUM_PASSWORD_LENGTH,
    requireEmailVerification: SETTINGS.AUTH.REQUIRE_EMAIL_VERIFICATION,
    sendResetPassword: async ({ user, url }) => {
      const { canSend, timeLeft } = await canSendEmail(user.id);
      if (!canSend) {
        throw new Error(
          `Please wait ${timeLeft} seconds before requesting another password reset email.`,
        );
        z;
      }

      await sendForgotPasswordMail({
        recipients: [user.email],
        subject: `${SETTINGS.MAIL.PREFIX} - Reset your password`,
        url,
      });

      await updateLastEmailSent(user.id);
    },
  },
  emailVerification: {
    sendVerificationEmail: async ({ user, url }) => {
      const { canSend, timeLeft } = await canSendEmail(user.id);
      if (!canSend) {
        throw new Error(
          `Please wait ${timeLeft} seconds before requesting another password reset email.`,
        );
      }

      await sendVerificationEmail({
        recipients: [user.email],
        subject: `${SETTINGS.MAIL.PREFIX} - Verify your email`,
        url,
      });

      await updateLastEmailSent(user.id);
    },
  },
  socialProviders: {
    google: {
      enabled: true,
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    },
  },
  hooks: {
    after: createAuthMiddleware(async (ctx) => {
      if (ctx.path == "/callback/:id") {
        const userId = ctx.context.newSession!.session!.userId;
        const provider = ctx.params.id;
        await gatewayLoginHandler({ userId, provider });
      }
      if (ctx.path == "/logout") {
        const gatewayUserClinet = await createUserClient();
        const { data, error } = await gatewayUserClinet.POST(
          "/api/account/auths/logout/",
        );
        console.log(data, error);
      }
    }),
  },
  plugins: [
    twoFactor(),
    username({
      minUsernameLength: SETTINGS.AUTH.MINIMUM_USERNAME_LENGTH,
      maxUsernameLength: SETTINGS.AUTH.MAXIMUM_USERNAME_LENGTH,
      usernameValidator: (username) => username !== "admin",
    }),
    anonymous(),
    passkey(),
    admin(),
    organization(),
  ],
});
