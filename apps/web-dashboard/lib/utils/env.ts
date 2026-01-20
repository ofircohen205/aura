/**
 * Environment variable validation and access.
 */

/**
 * Validates that required environment variables are set.
 * Throws an error if any required variable is missing.
 */
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

/**
 * Gets an environment variable with a default value.
 */
export function getEnv(key: string, defaultValue: string): string {
  return process.env[key] || defaultValue;
}

// Validate on module load (client-side only, skip in test environment)
if (typeof window !== "undefined" && process.env.NODE_ENV !== "test") {
  try {
    validateEnv();
  } catch (error) {
    // Log but don't throw - allow app to start with defaults
    console.warn("Environment validation warning:", error);
  }
}
