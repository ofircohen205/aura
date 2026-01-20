/**
 * Custom hook for handling form submissions with consistent error handling,
 * loading states, and success messages.
 */

import { useState, useCallback } from "react";
import { extractErrorMessage } from "@/lib/utils/error-handler";
import { logger } from "@/lib/utils/logger";

interface UseFormSubmissionOptions {
  onSuccess?: (data: unknown) => void;
  onError?: (error: string) => void;
  successMessage?: string;
  autoDismissSuccess?: number; // milliseconds, 0 to disable
}

export function useFormSubmission<T = unknown>(
  submitFn: (data: T) => Promise<unknown>,
  options: UseFormSubmissionOptions = {}
) {
  const { onSuccess, onError, successMessage, autoDismissSuccess = 5000 } = options;

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const submit = useCallback(
    async (data: T) => {
      setError(null);
      setSuccess(null);
      setIsLoading(true);

      try {
        const result = await submitFn(data);

        if (successMessage) {
          setSuccess(successMessage);

          // Auto-dismiss success message
          if (autoDismissSuccess > 0) {
            setTimeout(() => setSuccess(null), autoDismissSuccess);
          }
        }

        onSuccess?.(result);
        return result;
      } catch (err) {
        const errorMessage = extractErrorMessage(err);
        setError(errorMessage);
        logger.error("Form submission failed", err);
        onError?.(errorMessage);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [submitFn, onSuccess, onError, successMessage, autoDismissSuccess]
  );

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const clearSuccess = useCallback(() => {
    setSuccess(null);
  }, []);

  const clearAll = useCallback(() => {
    setError(null);
    setSuccess(null);
  }, []);

  return {
    submit,
    isLoading,
    error,
    success,
    clearError,
    clearSuccess,
    clearAll,
  };
}
