/**
 * ZAP:TODO
 * - Change the current config file to your own configuration
 * - Check `public/sw.js` file and change the URL in the `clients.openWindow` function
 */
import { Metadata } from "next";

import { ZapSettings } from "@/zap/types/zap.config.types";

export const VERCEL = process.env.VERCEL_ENV ? true : false;
export const DEV = process.env.NODE_ENV !== "production";

export const APP_NAME = "42 Bangkok";
export const APP_DESCRIPTION =
  "42 Bangkok is a student-run organization that provides a unique and innovative approach to education, focusing on peer-to-peer learning and project-based curriculum. Our mission is to empower students to become self-directed learners and problem solvers in a collaborative environment.";
export const BASE_URL = DEV
  ? "http://localhost:3000"
  : "https://app.42bangkok.com";

export const ZAP_DEFAULT_FLAGS = {
  VERCEL: {
    ENABLE_ANALYTICS: VERCEL,
    ENABLE_SPEED_INSIGHTS: VERCEL,
  },
  ENABLE_POSTHOG: false,
};

const AI_SYSTEM_PROMPT = "You are a helpful assistant.";

export const ZAP_DEFAULT_SETTINGS: ZapSettings = {
  AI: {
    SYSTEM_PROMPT: AI_SYSTEM_PROMPT,
  },
  AUTH: {
    REQUIRE_EMAIL_VERIFICATION: true,
    ENABLE_SOCIAL_PROVIDER: true,
    MINIMUM_USERNAME_LENGTH: 3,
    MAXIMUM_USERNAME_LENGTH: 20,
    MINIMUM_PASSWORD_LENGTH: 8,
    MAXIMUM_PASSWORD_LENGTH: 128,
    REDIRECT_URL_AFTER_SIGN_UP: "/login",
    REDIRECT_URL_AFTER_SIGN_IN: "/app",
  },
  NOTIFICATIONS: {
    VAPID_MAIL: "",
  },
  MAIL: {
    PREFIX: APP_NAME,
    RATE_LIMIT_SECONDS: 60,
  },
  PWA: {
    NAME: APP_NAME,
    SHORT_NAME: APP_NAME,
    DESCRIPTION: APP_DESCRIPTION,
    START_URL: "/",
    BACKGROUND_COLOR: "#ffffff",
    THEME_COLOR: "#000000",
    ICONS: [
      {
        src: "/icon-192x192.png",
        sizes: "192x192",
        type: "image/png",
      },
      {
        src: "/icon-512x512.png",
        sizes: "512x512",
        type: "image/png",
      },
    ],
  },
};

export const ZAP_DEFAULT_METADATA: Metadata = {
  title: APP_NAME,
  description: APP_DESCRIPTION,
  category: "technology",
  generator: "Next.js",
  applicationName: APP_NAME,
  referrer: "origin-when-cross-origin",
  keywords: [
    "Zap.ts",
    "typescript",
    "nextjs",
    "react",
    "boilerplate",
    "template",
    "web",
    "application",
  ],
  authors: [
    {
      name: "pumidol",
      url: "pumidol.com",
    },
  ],
  creator: "Pumidol Leeleredsakulvong",
  publisher: "Pumidol Leeleredsakulvong",
  metadataBase: new URL(BASE_URL),
  openGraph: {
    title: APP_NAME,
    description: APP_DESCRIPTION,
    url: BASE_URL,
    siteName: APP_NAME,
    images: [
      {
        url: `${BASE_URL}/og.png`,
        width: 1200,
        height: 630,
        alt: `${APP_NAME} Open Graph Image`,
      },
    ],
    locale: "en_US",
    type: "website",
  },
  robots: {
    index: true,
    follow: true,
    nocache: false,
    googleBot: {
      index: true,
      follow: true,
      noimageindex: false,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  icons: {
    icon: "/favicon.ico",
    apple: "/apple-touch-icon.png",
    shortcut: "/favicon.ico",
  },
  twitter: {
    card: "summary_large_image",
    title: APP_NAME,
    description: APP_DESCRIPTION,
    creator: "@42bangkok",
    images: [`${BASE_URL}/og.png`],
  },
  appleWebApp: {
    title: APP_NAME,
    statusBarStyle: "black-translucent",
    capable: true,
  },
  appLinks: {
    web: {
      url: "https://app.42bangkok.com",
      should_fallback: true,
    },
  },
};
