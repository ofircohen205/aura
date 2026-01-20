import * as React from "react";
import { cn } from "@/lib/utils/cn";

export type AlertVariant = "default" | "destructive" | "success" | "warning" | "info";

interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: AlertVariant;
}

const variantStyles: Record<AlertVariant, string> = {
  default: "border-border bg-background text-foreground",
  destructive: "border-destructive bg-destructive/10 text-destructive",
  success: "border-green-500 bg-green-50 text-green-800 dark:bg-green-950 dark:text-green-200",
  warning: "border-yellow-500 bg-yellow-50 text-yellow-800 dark:bg-yellow-950 dark:text-yellow-200",
  info: "border-blue-500 bg-blue-50 text-blue-800 dark:bg-blue-950 dark:text-blue-200",
};

export function Alert({ variant = "default", className, children, ...props }: AlertProps) {
  return (
    <div
      role="alert"
      className={cn("relative w-full rounded-lg border p-4", variantStyles[variant], className)}
      {...props}
    >
      {children}
    </div>
  );
}

export function AlertDescription({
  className,
  ...props
}: React.HTMLAttributes<HTMLParagraphElement>) {
  return <p className={cn("text-sm [&_p]:leading-relaxed", className)} {...props} />;
}
