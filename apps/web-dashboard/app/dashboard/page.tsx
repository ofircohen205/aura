"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/lib/hooks/useAuth";
import { ROUTES } from "@/lib/routes";
import { format } from "date-fns";

export default function DashboardPage() {
  const { user } = useAuth();
  const [formattedDate, setFormattedDate] = useState<string>("");

  useEffect(() => {
    if (user?.created_at) {
      setFormattedDate(format(new Date(user.created_at), "PP"));
    }
  }, [user?.created_at]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Welcome back{user ? `, ${user.username}` : ""}!</h1>
        <p className="text-muted-foreground">Here's an overview of your Aura dashboard</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Workflows</CardTitle>
            <CardDescription>Monitor and manage your workflows</CardDescription>
          </CardHeader>
          <CardContent>
            <Link href={ROUTES.DASHBOARD.WORKFLOWS}>
              <Button className="w-full">View Workflows</Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Audits</CardTitle>
            <CardDescription>View and manage code audit results</CardDescription>
          </CardHeader>
          <CardContent>
            <Link href={ROUTES.DASHBOARD.AUDITS}>
              <Button className="w-full">View Audits</Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Profile</CardTitle>
            <CardDescription>Manage your account information</CardDescription>
          </CardHeader>
          <CardContent>
            <Link href={ROUTES.DASHBOARD.PROFILE}>
              <Button className="w-full" variant="outline">
                View Profile
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>

      {user && (
        <Card>
          <CardHeader>
            <CardTitle>Account Information</CardTitle>
            <CardDescription>Your account details</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium text-muted-foreground">Email</label>
              <p className="text-sm">{user.email}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">Username</label>
              <p className="text-sm">{user.username}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">Status</label>
              <div className="flex items-center gap-2">
                <Badge variant={user.is_active ? "success" : "default"}>
                  {user.is_active ? "Active" : "Inactive"}
                </Badge>
                <Badge variant={user.is_verified ? "info" : "warning"}>
                  {user.is_verified ? "Verified" : "Unverified"}
                </Badge>
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">Member Since</label>
              <p className="text-sm">{formattedDate || "Loading..."}</p>
            </div>
            {user.roles && user.roles.length > 0 && (
              <div>
                <label className="text-sm font-medium text-muted-foreground">Roles</label>
                <div className="flex flex-wrap gap-2">
                  {user.roles.map((role: string) => (
                    <span
                      key={role}
                      className="rounded-full bg-secondary px-2 py-1 text-xs font-medium"
                    >
                      {role}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
