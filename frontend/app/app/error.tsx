"use client";

import { Button } from "@/components/ui/button";
import { AlertCircle } from "lucide-react";
import Link from "next/link";
import { useEffect } from "react";

export default function Error({
  error,
}: {
  error: Error & { digest?: string };
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error("An error occurred:", error);
  }, [error]);

  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <div className="text-center">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-red-100">
          <AlertCircle className="h-6 w-6 text-red-600" />
        </div>
        <h1 className="mt-4 text-3xl font-bold tracking-tight text-gray-900">
          Something went wrong!
        </h1>
        <p className="mt-2 text-base text-gray-600">
          An unexpected error occurred. Please try again or sign in.
        </p>
        <div className="mt-6 flex items-center justify-center">
          <Link href="/auth/login">
            <Button>Go to Sign In</Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
