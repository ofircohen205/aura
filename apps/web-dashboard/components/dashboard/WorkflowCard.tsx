"use client";

import { memo, useMemo } from "react";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { format } from "date-fns";
import { ROUTES } from "@/lib/routes";
import type { WorkflowResponse } from "@/types/api";

interface WorkflowCardProps {
  workflow: WorkflowResponse;
}

export const WorkflowCard = memo(function WorkflowCard({ workflow }: WorkflowCardProps) {
  const statusColors = useMemo(
    () => ({
      completed: "bg-green-500",
      failed: "bg-red-500",
      running: "bg-blue-500",
      pending: "bg-yellow-500",
    }),
    []
  );

  const statusColor = useMemo(() => {
    return statusColors[workflow.status as keyof typeof statusColors] || "bg-gray-500";
  }, [workflow.status, statusColors]);

  const formattedDate = useMemo(() => {
    return format(new Date(workflow.created_at), "PPp");
  }, [workflow.created_at]);

  const workflowType = useMemo(() => {
    return workflow.type;
  }, [workflow.type]);

  return (
    <Link href={ROUTES.DASHBOARD.WORKFLOW_DETAIL(workflow.thread_id)}>
      <Card className="transition-shadow hover:shadow-md">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">
              {workflowType} - {workflow.thread_id.slice(0, 8)}
            </CardTitle>
            <div
              className={`h-3 w-3 rounded-full ${statusColor}`}
              aria-label={`Workflow status: ${workflow.status}`}
              role="status"
            />
          </div>
          <CardDescription>{formattedDate}</CardDescription>
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
});
