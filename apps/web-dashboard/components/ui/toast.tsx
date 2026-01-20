"use client";

import { useEffect, useState } from "react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils/cn";

export type ToastType = "success" | "error" | "warning" | "info";

export interface Toast {
  id: string;
  message: string;
  type: ToastType;
  duration?: number; // milliseconds, 0 = no auto-dismiss
}

interface ToastProps {
  toast: Toast;
  onDismiss: (id: string) => void;
}

function ToastItem({ toast, onDismiss }: ToastProps) {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Trigger animation
    setIsVisible(true);

    // Auto-dismiss if duration is set
    if (toast.duration && toast.duration > 0) {
      const timer = setTimeout(() => {
        handleDismiss();
      }, toast.duration);

      return () => clearTimeout(timer);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [toast.duration]);

  const handleDismiss = () => {
    setIsVisible(false);
    // Wait for animation before removing
    setTimeout(() => {
      onDismiss(toast.id);
    }, 300);
  };

  const variantMap: Record<ToastType, "default" | "destructive" | "success" | "warning" | "info"> =
    {
      success: "success",
      error: "destructive",
      warning: "warning",
      info: "info",
    };

  return (
    <div
      className={cn(
        "min-w-[300px] max-w-md transition-all duration-300 ease-in-out",
        isVisible ? "opacity-100 translate-y-0" : "opacity-0 -translate-y-2"
      )}
      role="alert"
      aria-live={toast.type === "error" ? "assertive" : "polite"}
    >
      <Alert variant={variantMap[toast.type]}>
        <div className="flex items-start justify-between gap-4">
          <AlertDescription className="flex-1">{toast.message}</AlertDescription>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleDismiss}
            className="h-6 w-6 p-0"
            aria-label="Dismiss notification"
          >
            ×
          </Button>
        </div>
      </Alert>
    </div>
  );
}

interface ToastContainerProps {
  toasts: Toast[];
  onDismiss: (id: string) => void;
}

export function ToastContainer({ toasts, onDismiss }: ToastContainerProps) {
  if (toasts.length === 0) return null;

  return (
    <div
      className="fixed top-4 right-4 z-50 flex flex-col gap-2 pointer-events-none"
      aria-live="polite"
      aria-label="Notifications"
    >
      {toasts.map(toast => (
        <div key={toast.id} className="pointer-events-auto">
          <ToastItem toast={toast} onDismiss={onDismiss} />
        </div>
      ))}
    </div>
  );
}
