type LogLevel = "error" | "warn" | "info" | "debug";

interface LogContext {
  [key: string]: unknown;
}

class Logger {
  private isDevelopment = process.env.NODE_ENV === "development";

  private log(level: LogLevel, message: string, error?: unknown, context?: LogContext) {
    if (!this.isDevelopment && level === "debug") {
      return;
    }

    const timestamp = new Date().toISOString();
    const errorData: Record<string, unknown> = {};
    if (error) {
      errorData.error = error instanceof Error ? error.message : String(error);
      if (error instanceof Error && error.stack) {
        errorData.stack = error.stack;
      }
    }
    const logEntry = {
      timestamp,
      level,
      message,
      ...errorData,
      ...(context || {}),
    };

    switch (level) {
      case "error":
        console.error(`[${timestamp}] ERROR:`, message, error || "", context || "");
        break;
      case "warn":
        console.warn(`[${timestamp}] WARN:`, message, context || "");
        break;
      case "info":
        if (this.isDevelopment) {
          console.info(`[${timestamp}] INFO:`, message, context || "");
        }
        break;
      case "debug":
        if (this.isDevelopment) {
          console.debug(`[${timestamp}] DEBUG:`, message, context || "");
        }
        break;
    }
  }

  error(message: string, error?: unknown, context?: LogContext) {
    this.log("error", message, error, context);
  }

  warn(message: string, context?: LogContext) {
    this.log("warn", message, undefined, context);
  }

  info(message: string, context?: LogContext) {
    this.log("info", message, undefined, context);
  }

  debug(message: string, context?: LogContext) {
    this.log("debug", message, undefined, context);
  }
}

export const logger = new Logger();
