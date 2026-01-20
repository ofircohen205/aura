export function validateEnv() {
  const required = ["NEXT_PUBLIC_API_URL"] as const;
  const missing: string[] = [];

  for (const key of required) {
    if (!process.env[key]) {
      missing.push(key);
    }
  }

  if (missing.length > 0) {
    throw new Error(`Missing required environment variables: ${missing.join(", ")}`);
  }
}

export function getEnv(key: string, defaultValue: string): string {
  return process.env[key] || defaultValue;
}

if (typeof window !== "undefined" && process.env.NODE_ENV !== "test") {
  try {
    validateEnv();
  } catch (error) {
    console.warn("Environment validation warning:", error);
  }
}
