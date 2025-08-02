import { createUserClient } from "../clients";

export async function getMe() {
  const client = await createUserClient();
  const { data, error } = await client.GET("/api/account/users/me/");
  if (error) {
    throw new Error(`Failed to fetch user`);
  }
  return data;
}
