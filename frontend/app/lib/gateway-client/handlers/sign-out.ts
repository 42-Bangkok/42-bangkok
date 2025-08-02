import { createUserClient } from "../clients";

export interface IGatewayLoginHandler {
  userId: string;
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
export async function gatewaySignOutHandler() {
  const client = await createUserClient();
  const { error } = await client.POST("/api/account/auths/logout/");
  if (error) {
    console.error("Error logging out from gateway:", error);
    throw new Error("Failed to log out from gateway");
  }
}
