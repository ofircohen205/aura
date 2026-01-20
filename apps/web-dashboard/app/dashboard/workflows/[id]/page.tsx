"use client";

import { use } from "react";
import { useParams } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { format } from "date-fns";
import type { WorkflowResponse } from "@/types/api";

export default function WorkflowDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const workflow: WorkflowResponse & { created_at?: string; type?: string } = {
    thread_id: id,
    status: "completed",
    state: {},
    created_at: new Date().toISOString(),
    type: "Workflow",
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Workflow Details</h1>
        <p className="text-muted-foreground">Thread ID: {workflow.thread_id}</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Status</CardTitle>
            <CardDescription>Current workflow status</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <div
                className={`h-3 w-3 rounded-full ${
                  workflow.status === "completed"
                    ? "bg-green-500"
                    : workflow.status === "failed"
                      ? "bg-red-500"
                      : "bg-yellow-500"
                }`}
              />
              <span className="font-medium capitalize">{workflow.status}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Type</CardTitle>
            <CardDescription>Workflow type</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="font-medium">{workflow.type || "Unknown"}</p>
          </CardContent>
        </Card>

        {workflow.created_at && (
          <Card>
            <CardHeader>
              <CardTitle>Created At</CardTitle>
              <CardDescription>When this workflow was created</CardDescription>
            </CardHeader>
            <CardContent>
              <p>{format(new Date(workflow.created_at), "PPp")}</p>
            </CardContent>
          </Card>
        )}

        {workflow.state && Object.keys(workflow.state).length > 0 && (
          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle>State</CardTitle>
              <CardDescription>Workflow execution state</CardDescription>
            </CardHeader>
            <CardContent>
              <pre className="overflow-auto rounded-md bg-muted p-4 text-sm">
                {JSON.stringify(workflow.state, null, 2)}
              </pre>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
