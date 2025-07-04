import type { Provider } from "@/zap.config";

export interface ZapSettings {
  AI: {
    SYSTEM_PROMPT: string;
    CHAT?: {
      MAX_TOKENS?: number;
      TEMPERATURE?: number;
      PRESENCE_PENALTY?: number;
      FREQUENCY_PENALTY?: number;
      STOP_SEQUENCES?: string[];
      MAX_RETRIES?: number;
    };
    COMPLETION?: {
      MAX_TOKENS?: number;
      TEMPERATURE?: number;
      PRESENCE_PENALTY?: number;
      FREQUENCY_PENALTY?: number;
      STOP_SEQUENCES?: string[];
      MAX_RETRIES?: number;
    };
  };
  AUTH: {
    REQUIRE_MAIL_VERIFICATION: boolean;
    ENABLE_SOCIAL_PROVIDER: boolean;
    MINIMUM_USERNAME_LENGTH: number;
    MAXIMUM_USERNAME_LENGTH: number;
    MINIMUM_PASSWORD_LENGTH: number;
    MAXIMUM_PASSWORD_LENGTH: number;
    LOGIN_URL: string;
    REDIRECT_URL_AFTER_SIGN_UP: string;
    REDIRECT_URL_AFTER_SIGN_IN: string;
    PROVIDERS: Provider[];
    PASSWORD_COMPROMISED_MESSAGE: string;
    PUBLIC_PATHS: string[];
  };
  BLOG: {
    BASE_PATH: string;
  };
  MAIL: {
    PREFIX: string;
    RATE_LIMIT_SECONDS: number;
    FROM: string;
  };
  NOTIFICATIONS: {
    VAPID_MAIL?: string;
  };
  PWA: {
    NAME: string;
    SHORT_NAME: string;
    DESCRIPTION: string;
    START_URL: string;
    BACKGROUND_COLOR: string;
    THEME_COLOR: string;
    ICONS: Array<{
      src: string;
      sizes: string;
      type: string;
    }>;
  };
  WAITLIST: {
    TITLE: string;
    DESCRIPTION: string;
    SHOW_COUNT: boolean;
  };
}
