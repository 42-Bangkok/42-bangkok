import { headers } from "next/headers";

import { auth } from "@/zap/lib/auth/server";

export default async function TestPage() {
  const session = await auth.api.getSession({
    headers: await headers(), // you need to pass the headers object.
  });
  console.log("Session:", session);
  return (
    <div>
      <h1>Test Page</h1>
      <p>This is a test page for authenticated users only.</p>
      <pre>{JSON.stringify(session, null, 2)}</pre>
    </div>
  );
}
