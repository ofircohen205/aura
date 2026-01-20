"use client";

import { use } from "react";
import { useParams } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { format } from "date-fns";
import type { AuditResponse } from "@/types/api";

export default function AuditDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  // In a real implementation, fetch audit details by ID
  const audit: AuditResponse & { id: string; created_at: string; violations?: string[] } = {
    id,
    status: "completed",
    repo: "example/repo",
    message: "Audit completed successfully",
    created_at: new Date().toISOString(),
    violations: [],
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Audit Details</h1>
        <p className="text-muted-foreground">Audit ID: {audit.id}</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Repository</CardTitle>
            <CardDescription>Audited repository path</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="font-medium">{audit.repo}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Status</CardTitle>
            <CardDescription>Audit execution status</CardDescription>
          </CardHeader>
          <CardContent>
            <span
              className={`inline-block rounded-full px-3 py-1 text-sm font-medium ${
                audit.status === "completed"
                  ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                  : audit.status === "failed"
                    ? "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
                    : "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200"
              }`}
            >
              {audit.status}
            </span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Created At</CardTitle>
            <CardDescription>When this audit was created</CardDescription>
          </CardHeader>
          <CardContent>
            <p>{format(new Date(audit.created_at), "PPp")}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Message</CardTitle>
            <CardDescription>Audit result message</CardDescription>
          </CardHeader>
          <CardContent>
            <p>{audit.message}</p>
          </CardContent>
        </Card>
      </div>

      {audit.violations && audit.violations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Violations</CardTitle>
            <CardDescription>
              {audit.violations.length} violation{audit.violations.length !== 1 ? "s" : ""} found
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {audit.violations.map((violation: string, index: number) => (
                <li key={index} className="rounded-md bg-destructive/10 p-3 text-sm">
                  {violation}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {(!audit.violations || audit.violations.length === 0) && (
        <Card>
          <CardContent className="py-8 text-center text-muted-foreground">
            No violations found. Code audit passed!
          </CardContent>
        </Card>
      )}
    </div>
  );
}
