"use client";

// This component is deprecated.
// The full challenge form is now at /app/generate/page.tsx
// This stub is kept so nothing breaks if accidentally imported.

import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function ChallengeForm() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/generate");
  }, [router]);
  return null;
}