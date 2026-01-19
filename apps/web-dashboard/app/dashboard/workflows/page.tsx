"use client";

import { useState, useEffect } from "react";
import { WorkflowCard } from "@/components/dashboard/WorkflowCard";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { workflowsApi } from "@/lib/api/workflows";
import type { WorkflowResponse, StruggleInput, AuditInput } from "@/types/api";

// Mock data for now - will be replaced with actual API calls
const mockWorkflows: (WorkflowResponse & { created_at: string; type: string })[] = [];

export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState(mockWorkflows);
  const [isLoading, setIsLoading] = useState(false);
  const [showStruggleForm, setShowStruggleForm] = useState(false);
  const [showAuditForm, setShowAuditForm] = useState(false);
  const [struggleData, setStruggleData] = useState<StruggleInput>({
    edit_frequency: 0,
    error_logs: [],
    history: [],
  });
  const [auditData, setAuditData] = useState<AuditInput>({
    diff_content: "",
    violations: [],
  });

  const handleTriggerStruggle = async () => {
    try {
      setIsLoading(true);
      const result = await workflowsApi.triggerStruggle(struggleData);
      setWorkflows([
        ...workflows,
        { ...result, created_at: new Date().toISOString(), type: "Struggle Detection" },
      ]);
      setShowStruggleForm(false);
      setStruggleData({ edit_frequency: 0, error_logs: [], history: [] });
    } catch (error) {
      console.error("Failed to trigger struggle workflow:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTriggerAudit = async () => {
    try {
      setIsLoading(true);
      const result = await workflowsApi.triggerAudit(auditData);
      setWorkflows([
        ...workflows,
        { ...result, created_at: new Date().toISOString(), type: "Code Audit" },
      ]);
      setShowAuditForm(false);
      setAuditData({ diff_content: "", violations: [] });
    } catch (error) {
      console.error("Failed to trigger audit workflow:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Workflows</h1>
          <p className="text-muted-foreground">Monitor and manage your workflows</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => setShowStruggleForm(!showStruggleForm)} variant="outline">
            Trigger Struggle Detection
          </Button>
          <Button onClick={() => setShowAuditForm(!showAuditForm)} variant="outline">
            Trigger Code Audit
          </Button>
        </div>
      </div>

      {showStruggleForm && (
        <Card>
          <CardHeader>
            <CardTitle>Trigger Struggle Detection Workflow</CardTitle>
            <CardDescription>
              Analyze edit patterns to detect if a user is struggling
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium">Edit Frequency</label>
              <Input
                type="number"
                step="0.1"
                value={struggleData.edit_frequency}
                onChange={e =>
                  setStruggleData({ ...struggleData, edit_frequency: parseFloat(e.target.value) })
                }
              />
            </div>
            <div>
              <label className="text-sm font-medium">Error Logs (one per line)</label>
              <textarea
                className="flex h-24 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={struggleData.error_logs.join("\n")}
                onChange={e =>
                  setStruggleData({
                    ...struggleData,
                    error_logs: e.target.value.split("\n").filter(line => line.trim()),
                  })
                }
              />
            </div>
            <div className="flex gap-2">
              <Button onClick={handleTriggerStruggle} disabled={isLoading}>
                {isLoading ? "Triggering..." : "Trigger Workflow"}
              </Button>
              <Button variant="outline" onClick={() => setShowStruggleForm(false)}>
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {showAuditForm && (
        <Card>
          <CardHeader>
            <CardTitle>Trigger Code Audit Workflow</CardTitle>
            <CardDescription>Perform static analysis on code changes</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium">Diff Content</label>
              <textarea
                className="flex h-32 w-full rounded-md border border-input bg-background px-3 py-2 text-sm font-mono"
                value={auditData.diff_content}
                onChange={e => setAuditData({ ...auditData, diff_content: e.target.value })}
                placeholder="Paste git diff content here..."
              />
            </div>
            <div className="flex gap-2">
              <Button onClick={handleTriggerAudit} disabled={isLoading}>
                {isLoading ? "Triggering..." : "Trigger Workflow"}
              </Button>
              <Button variant="outline" onClick={() => setShowAuditForm(false)}>
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <div>
        <h2 className="mb-4 text-xl font-semibold">Recent Workflows</h2>
        {workflows.length === 0 ? (
          <Card>
            <CardContent className="py-8 text-center text-muted-foreground">
              No workflows yet. Trigger a workflow to get started.
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {workflows.map(workflow => (
              <WorkflowCard key={workflow.thread_id} workflow={workflow} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
