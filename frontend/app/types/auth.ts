// Extended types for better-auth with custom session data
export interface ExtendedUser {
  id: string;
  name: string;
  email: string;
  emailVerified: boolean;
  createdAt: Date;
  updatedAt: Date;
  image?: string | null;
  gatewayToken: string;
}

export interface ExtendedSession {
  id: string;
  token: string;
  expiresAt: Date;
  createdAt: Date;
  updatedAt: Date;
  ipAddress?: string;
  userAgent?: string;
  userId: string;
}

export interface CustomSessionData {
  user: ExtendedUser;
  session: ExtendedSession;
}
