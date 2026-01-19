"use client";

import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { format } from "date-fns";
import type { WorkflowResponse } from "@/types/api";

interface WorkflowCardProps {
  workflow: WorkflowResponse & { created_at?: string; type?: string };
}

export function WorkflowCard({ workflow }: WorkflowCardProps) {
  const statusColors = {
    completed: "bg-green-500",
    failed: "bg-red-500",
    running: "bg-blue-500",
    pending: "bg-yellow-500",
  };

  const statusColor = statusColors[workflow.status as keyof typeof statusColors] || "bg-gray-500";

  return (
    <Link href={`/dashboard/workflows/${workflow.thread_id}`}>
      <Card className="transition-shadow hover:shadow-md">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">
              {workflow.type || "Workflow"} - {workflow.thread_id.slice(0, 8)}
            </CardTitle>
            <div className={`h-3 w-3 rounded-full ${statusColor}`} aria-label={workflow.status} />
          </div>
          <CardDescription>
            {workflow.created_at
              ? format(new Date(workflow.created_at), "PPp")
              : "No timestamp available"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Status:</span>
              <span className="font-medium capitalize">{workflow.status}</span>
            </div>
            {workflow.state && (
              <div className="text-sm text-muted-foreground">
                {Object.keys(workflow.state).length} state entries
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
