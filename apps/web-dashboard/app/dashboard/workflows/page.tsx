"use client";

import { useState, useEffect, useCallback, useMemo } from "react";
import { WorkflowCard } from "@/components/dashboard/WorkflowCard";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { workflowsApi } from "@/lib/api/workflows";
import { extractErrorMessage } from "@/lib/utils/error-handler";
import { logger } from "@/lib/utils/logger";
import { useToastContext } from "@/components/ToastProvider";
import type { WorkflowResponse, StruggleInput, AuditInput } from "@/types/api";

export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState<WorkflowResponse[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isFetching, setIsFetching] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
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

  useEffect(() => {
    let isCancelled = false;

    const fetchWorkflows = async () => {
      try {
        setIsFetching(true);
        setError(null);
        const response = await workflowsApi.list();

        if (isCancelled) return;

        const transformedWorkflows = response.items;
        setWorkflows(transformedWorkflows);
      } catch (err) {
        if (isCancelled) return;
        const errorMessage = extractErrorMessage(err);
        setError(errorMessage);
        logger.error("Failed to fetch workflows", err);
      } finally {
        if (!isCancelled) {
          setIsFetching(false);
        }
      }
    };

    fetchWorkflows();

    return () => {
      isCancelled = true;
    };
  }, []);

  const handleTriggerStruggle = useCallback(async () => {
    setError(null);
    setSuccess(null);

    const optimisticId = `temp-${Date.now()}`;
    const optimisticWorkflow: WorkflowResponse = {
      thread_id: optimisticId,
      status: "pending",
      created_at: new Date().toISOString(),
      type: "Struggle Detection",
    };

    setWorkflows(prev => [...prev, optimisticWorkflow]);
    setShowStruggleForm(false);

    try {
      setIsLoading(true);
      const result = await workflowsApi.triggerStruggle(struggleData);

      setWorkflows(prev => prev.map(w => (w.thread_id === optimisticId ? result : w)));

      setStruggleData({ edit_frequency: 0, error_logs: [], history: [] });
      setSuccess("Struggle detection workflow triggered successfully");

      setTimeout(() => setSuccess(null), 5000);
    } catch (err) {
      setWorkflows(prev => prev.filter(w => w.thread_id !== optimisticId));
      const errorMessage = extractErrorMessage(err);
      setError(errorMessage);
      logger.error("Failed to trigger struggle workflow", err);
      setShowStruggleForm(true); // Re-show form on error
    } finally {
      setIsLoading(false);
    }
  }, [struggleData]);

  const handleTriggerAudit = useCallback(async () => {
    setError(null);
    setSuccess(null);

    const optimisticId = `temp-${Date.now()}`;
    const optimisticWorkflow: WorkflowResponse = {
      thread_id: optimisticId,
      status: "pending",
      created_at: new Date().toISOString(),
      type: "Code Audit",
    };

    setWorkflows(prev => [...prev, optimisticWorkflow]);
    setShowAuditForm(false);

    try {
      setIsLoading(true);
      const result = await workflowsApi.triggerAudit(auditData);

      setWorkflows(prev => prev.map(w => (w.thread_id === optimisticId ? result : w)));

      setAuditData({ diff_content: "", violations: [] });
      setSuccess("Code audit workflow triggered successfully");

      setTimeout(() => setSuccess(null), 5000);
    } catch (err) {
      setWorkflows(prev => prev.filter(w => w.thread_id !== optimisticId));
      const errorMessage = extractErrorMessage(err);
      setError(errorMessage);
      logger.error("Failed to trigger audit workflow", err);
      setShowAuditForm(true); // Re-show form on error
    } finally {
      setIsLoading(false);
    }
  }, [auditData]);

  return (
    <div className="space-y-6">
      {error && (
        <Alert variant="destructive" role="alert">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
      {success && (
        <Alert variant="success" role="status" aria-live="polite">
          <AlertDescription>{success}</AlertDescription>
        </Alert>
      )}

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
            <div className="space-y-2">
              <Label htmlFor="edit-frequency">Edit Frequency</Label>
              <Input
                id="edit-frequency"
                type="number"
                step="0.1"
                min="0"
                value={struggleData.edit_frequency}
                onChange={e => {
                  const value = parseFloat(e.target.value);
                  if (!isNaN(value) && value >= 0) {
                    setStruggleData({ ...struggleData, edit_frequency: value });
                  }
                }}
                aria-required="false"
                aria-describedby="edit-frequency-help"
              />
              <p id="edit-frequency-help" className="text-xs text-muted-foreground">
                Number of edits per time period
              </p>
            </div>
            <div className="space-y-2">
              <Label htmlFor="error-logs">Error Logs (one per line)</Label>
              <Textarea
                id="error-logs"
                className="min-h-[96px]"
                value={struggleData.error_logs.join("\n")}
                onChange={e =>
                  setStruggleData({
                    ...struggleData,
                    error_logs: e.target.value.split("\n").filter(line => line.trim()),
                  })
                }
                placeholder="Enter error messages, one per line"
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
            <div className="space-y-2">
              <Label htmlFor="diff-content">Diff Content</Label>
              <Textarea
                id="diff-content"
                className="min-h-[128px] font-mono"
                value={auditData.diff_content}
                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
                  setAuditData({ ...auditData, diff_content: e.target.value })
                }
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
        {isFetching ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3].map(i => (
              <Card key={i}>
                <CardHeader>
                  <Skeleton className="h-6 w-32" />
                  <Skeleton className="h-4 w-24 mt-2" />
                </CardHeader>
                <CardContent>
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-3/4 mt-2" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : workflows.length === 0 ? (
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
