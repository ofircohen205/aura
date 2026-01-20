"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/lib/hooks/useAuth";
import { useRouter } from "next/navigation";
import { logger } from "@/lib/utils/logger";
import { ROUTES } from "@/lib/routes";

export default function SettingsPage() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  const handleLogout = async () => {
    setIsLoading(true);
    try {
      await logout();
      router.push(ROUTES.AUTH.LOGIN);
    } catch (error) {
      logger.error("Logout failed", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="text-muted-foreground">Manage your account settings and preferences</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Preferences</CardTitle>
          <CardDescription>Customize your dashboard experience</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium text-muted-foreground">Theme (Coming Soon)</label>
            <p className="mt-1 text-sm text-muted-foreground">
              Theme customization will be available in a future update.
            </p>
          </div>
          <div>
            <label className="text-sm font-medium text-muted-foreground">
              Notifications (Coming Soon)
            </label>
            <p className="mt-1 text-sm text-muted-foreground">
              Notification preferences will be available in a future update.
            </p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Security</CardTitle>
          <CardDescription>Manage your account security settings</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium text-muted-foreground">
              Password (Coming Soon)
            </label>
            <p className="mt-1 text-sm text-muted-foreground">
              Password change functionality will be available in a future update.
            </p>
          </div>
          <div>
            <label className="text-sm font-medium text-muted-foreground">
              Two-Factor Authentication (Coming Soon)
            </label>
            <p className="mt-1 text-sm text-muted-foreground">
              Two-factor authentication will be available in a future update.
            </p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>API Access</CardTitle>
          <CardDescription>Manage API tokens and access</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium text-muted-foreground">
              API Tokens (Coming Soon)
            </label>
            <p className="mt-1 text-sm text-muted-foreground">
              API token management will be available in a future update.
            </p>
          </div>
        </CardContent>
      </Card>

      <Card className="border-destructive">
        <CardHeader>
          <CardTitle>Danger Zone</CardTitle>
          <CardDescription>Irreversible and destructive actions</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium">Sign Out</label>
            <p className="mt-1 text-sm text-muted-foreground">
              Sign out of your account. You will need to log in again to access the dashboard.
            </p>
            <Button
              variant="destructive"
              className="mt-4"
              onClick={handleLogout}
              disabled={isLoading}
            >
              {isLoading ? "Signing out..." : "Sign Out"}
            </Button>
          </div>
          <div>
            <label className="text-sm font-medium">Delete Account (Coming Soon)</label>
            <p className="mt-1 text-sm text-muted-foreground">
              Permanently delete your account and all associated data. This action cannot be undone.
            </p>
            <Button variant="destructive" className="mt-4" disabled>
              Delete Account
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
