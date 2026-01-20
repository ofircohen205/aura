"use client";

import { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/lib/hooks/useAuth";
import { authApi } from "@/lib/api/auth";
import { extractErrorMessage } from "@/lib/utils/error-handler";
import { format } from "date-fns";
import type { UserUpdate } from "@/types/api";

export default function ProfilePage() {
  const { user, fetchUser } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState<UserUpdate>({
    username: "",
    email: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    if (user) {
      setFormData({
        username: user.username || "",
        email: user.email || "",
      });
    }
  }, [user]);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      setError(null);
      setSuccess(null);
      setIsLoading(true);

      try {
        await authApi.updateUser(formData);
        await fetchUser();
        setSuccess("Profile updated successfully");
        setIsEditing(false);

        setTimeout(() => setSuccess(null), 5000);
      } catch (err) {
        setError(extractErrorMessage(err));
      } finally {
        setIsLoading(false);
      }
    },
    [formData, fetchUser]
  );

  const handleCancel = useCallback(() => {
    if (user) {
      setFormData({
        username: user.username || "",
        email: user.email || "",
      });
    }
    setIsEditing(false);
    setError(null);
    setSuccess(null);
  }, [user]);

  if (!user) {
    return (
      <div
        className="flex min-h-[400px] items-center justify-center"
        role="status"
        aria-live="polite"
      >
        <p className="text-muted-foreground">Loading profile...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Profile</h1>
        <p className="text-muted-foreground">Manage your account information</p>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert variant="success" role="status" aria-live="polite">
          <AlertDescription>{success}</AlertDescription>
        </Alert>
      )}

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Account Information</CardTitle>
              <CardDescription>Update your profile details</CardDescription>
            </div>
            {!isEditing && (
              <Button variant="outline" onClick={() => setIsEditing(true)}>
                Edit Profile
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {isEditing ? (
            <form onSubmit={handleSubmit} className="space-y-4" aria-label="Update profile form">
              <div className="space-y-2">
                <Label htmlFor="username">Username</Label>
                <Input
                  id="username"
                  type="text"
                  value={formData.username}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                    setFormData({ ...formData, username: e.target.value })
                  }
                  required
                  aria-required="true"
                  aria-describedby={error ? "username-error" : undefined}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                    setFormData({ ...formData, email: e.target.value })
                  }
                  required
                  aria-required="true"
                  aria-describedby={error ? "email-error" : undefined}
                />
              </div>
              <div className="flex gap-2">
                <Button type="submit" disabled={isLoading}>
                  {isLoading ? "Saving..." : "Save Changes"}
                </Button>
                <Button type="button" variant="outline" onClick={handleCancel}>
                  Cancel
                </Button>
              </div>
            </form>
          ) : (
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-muted-foreground">Username</label>
                <p className="text-sm">{user.username}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-muted-foreground">Email</label>
                <p className="text-sm">{user.email}</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Account Status</CardTitle>
          <CardDescription>Your account status and verification</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium text-muted-foreground">Account Status</label>
            <div className="mt-1 flex items-center gap-2">
              <Badge variant={user.is_active ? "success" : "default"}>
                {user.is_active ? "Active" : "Inactive"}
              </Badge>
              <Badge variant={user.is_verified ? "info" : "warning"}>
                {user.is_verified ? "Verified" : "Unverified"}
              </Badge>
            </div>
          </div>
          {user.roles && user.roles.length > 0 && (
            <div>
              <label className="text-sm font-medium text-muted-foreground">Roles</label>
              <div className="mt-1 flex flex-wrap gap-2">
                {user.roles.map((role: string) => (
                  <span
                    key={role}
                    className="rounded-full bg-secondary px-3 py-1 text-xs font-medium"
                  >
                    {role}
                  </span>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Account Details</CardTitle>
          <CardDescription>Account creation and update information</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium text-muted-foreground">User ID</label>
            <p className="text-sm font-mono">{user.id}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-muted-foreground">Member Since</label>
            <p className="text-sm">{format(new Date(user.created_at), "PPp")}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-muted-foreground">Last Updated</label>
            <p className="text-sm">{format(new Date(user.updated_at), "PPp")}</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
