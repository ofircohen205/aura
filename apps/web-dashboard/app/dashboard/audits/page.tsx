"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { auditsApi } from "@/lib/api/audits";
import { extractErrorMessage } from "@/lib/utils/error-handler";
import { logger } from "@/lib/utils/logger";
import { format } from "date-fns";
import { ROUTES } from "@/lib/routes";
import type { AuditResponse } from "@/types/api";

export default function AuditsPage() {
  const [audits, setAudits] = useState<
    (AuditResponse & { id: string; created_at: string; violations?: string[] })[]
  >([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isFetching, setIsFetching] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [showTriggerForm, setShowTriggerForm] = useState(false);
  const [repoPath, setRepoPath] = useState("");

  // Fetch audits on component mount
  useEffect(() => {
    let isCancelled = false;

    const fetchAudits = async () => {
      try {
        setIsFetching(true);
        setError(null);
        const response = await auditsApi.list();

        // Don't update state if component unmounted
        if (isCancelled) return;

        // Transform API response to ensure required fields are present
        const transformedAudits = response.items.map((audit, index) => ({
          ...audit,
          id: audit.id || `audit-${Date.now()}-${index}`,
          created_at: audit.created_at || new Date().toISOString(),
          violations: audit.violations || [],
        }));
        setAudits(transformedAudits);
      } catch (err) {
        if (isCancelled) return;
        const errorMessage = extractErrorMessage(err);
        setError(errorMessage);
        logger.error("Failed to fetch audits", err);
      } finally {
        if (!isCancelled) {
          setIsFetching(false);
        }
      }
    };

    fetchAudits();

    // Cleanup function to prevent state updates after unmount
    return () => {
      isCancelled = true;
    };
  }, []);

  const handleTriggerAudit = useCallback(async () => {
    if (!repoPath.trim()) return;

    setError(null);
    setSuccess(null);

    try {
      setIsLoading(true);
      const result = await auditsApi.triggerAudit(repoPath);
      setAudits(prev => [
        ...prev,
        {
          ...result,
          id: result.id || `audit-${Date.now()}`,
          created_at: result.created_at || new Date().toISOString(),
          violations: result.violations || [],
        },
      ]);
      setShowTriggerForm(false);
      setRepoPath("");
      setSuccess("Audit triggered successfully");

      // Auto-dismiss success message after 5 seconds
      setTimeout(() => setSuccess(null), 5000);
    } catch (err) {
      const errorMessage = extractErrorMessage(err);
      setError(errorMessage);
      logger.error("Failed to trigger audit", err);
    } finally {
      setIsLoading(false);
    }
  }, [repoPath]);

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
          <h1 className="text-3xl font-bold">Audits</h1>
          <p className="text-muted-foreground">View and manage code audit results</p>
        </div>
        <Button onClick={() => setShowTriggerForm(!showTriggerForm)} variant="outline">
          Trigger New Audit
        </Button>
      </div>

      {showTriggerForm && (
        <Card>
          <CardHeader>
            <CardTitle>Trigger Code Audit</CardTitle>
            <CardDescription>Audit a repository for code violations</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="repo-path">Repository Path</Label>
              <Input
                id="repo-path"
                type="text"
                value={repoPath}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setRepoPath(e.target.value)}
                placeholder="/path/to/repository"
                required
                aria-required="true"
                aria-describedby="repo-path-help"
                pattern="^/.+"
                title="Repository path must start with /"
              />
              <p id="repo-path-help" className="text-xs text-muted-foreground">
                Absolute path to the repository to audit (e.g., /path/to/repository)
              </p>
            </div>
            <div className="flex gap-2">
              <Button onClick={handleTriggerAudit} disabled={isLoading || !repoPath.trim()}>
                {isLoading ? "Triggering..." : "Trigger Audit"}
              </Button>
              <Button variant="outline" onClick={() => setShowTriggerForm(false)}>
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <div>
        <h2 className="mb-4 text-xl font-semibold">Recent Audits</h2>
        {isFetching ? (
          <div className="space-y-4">
            {[1, 2, 3].map(i => (
              <Card key={i}>
                <CardHeader>
                  <Skeleton className="h-6 w-48" />
                  <Skeleton className="h-4 w-32 mt-2" />
                </CardHeader>
                <CardContent>
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-2/3 mt-2" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : audits.length === 0 ? (
          <Card>
            <CardContent className="py-8 text-center text-muted-foreground">
              No audits yet. Trigger an audit to get started.
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {audits.map(audit => (
              <Link key={audit.id} href={ROUTES.DASHBOARD.AUDIT_DETAIL(audit.id)}>
                <Card className="transition-shadow hover:shadow-md">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle>{audit.repo}</CardTitle>
                      <Badge
                        variant={
                          audit.status === "completed"
                            ? "success"
                            : audit.status === "failed"
                              ? "error"
                              : "warning"
                        }
                      >
                        {audit.status}
                      </Badge>
                    </div>
                    <CardDescription>
                      {audit.created_at
                        ? format(new Date(audit.created_at), "PPp")
                        : "No date available"}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">{audit.message}</p>
                    {audit.violations && audit.violations.length > 0 && (
                      <p className="mt-2 text-sm">
                        {audit.violations.length} violation
                        {audit.violations.length !== 1 ? "s" : ""} found
                      </p>
                    )}
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
