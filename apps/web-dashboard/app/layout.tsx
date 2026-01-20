import type { Metadata } from "next";
import "./globals.css";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { ToastProvider } from "@/components/ToastProvider";

export const metadata: Metadata = {
  title: "Aura Dashboard",
  description: "AI-powered code analysis and learning platform",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body suppressHydrationWarning>
        <ErrorBoundary>
          <ToastProvider>
            <a href="#main-content" className="skip-to-main">
              Skip to main content
            </a>
            {children}
          </ToastProvider>
        </ErrorBoundary>
      </body>
    </html>
  );
}
