"use client";

import { useState, useEffect } from "react";
import { AxiosError } from "axios";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { ragApi, RAGStatsResponse } from "@/lib/api/rag";
import { useToast } from "@/lib/hooks/useToast";

export default function RAGExplorerPage() {
  const { error: showError } = useToast();
  const [query, setQuery] = useState("");
  const [errorPatterns, setErrorPatterns] = useState("");
  const [topK, setTopK] = useState(5);
  const [results, setResults] = useState<string | null>(null);
  const [stats, setStats] = useState<RAGStatsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingStats, setIsLoadingStats] = useState(false);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    setIsLoadingStats(true);
    try {
      const statsData = await ragApi.getStats();
      setStats(statsData);
    } catch (error) {
      const axiosError = error as AxiosError<{ detail?: string }>;
      showError(axiosError.response?.data?.detail || "Failed to load RAG statistics");
    } finally {
      setIsLoadingStats(false);
    }
  };

  const handleQuery = async () => {
    if (!query.trim()) {
      showError("Please enter a query");
      return;
    }

    setIsLoading(true);
    setResults(null);

    try {
      const errorPatternsList = errorPatterns
        .split("\n")
        .map(p => p.trim())
        .filter(p => p.length > 0);

      const response = await ragApi.query({
        query: query.trim(),
        error_patterns: errorPatternsList.length > 0 ? errorPatternsList : undefined,
        top_k: topK,
      });

      setResults(response.context);
    } catch (error) {
      const axiosError = error as AxiosError<{ detail?: string }>;
      showError(axiosError.response?.data?.detail || "Failed to query RAG");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">RAG Explorer</h1>
        <p className="text-muted-foreground">
          Explore and query the vector database for educational lessons and documentation
        </p>
      </div>

      {/* Statistics Card */}
      <Card>
        <CardHeader>
          <CardTitle>Vector Store Statistics</CardTitle>
          <CardDescription>Overview of documents in the RAG vector database</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoadingStats ? (
            <LoadingSpinner />
          ) : stats ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <div>
                <Label className="text-muted-foreground">Total Documents</Label>
                <p className="text-2xl font-bold">{stats.total_documents}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Total Chunks</Label>
                <p className="text-2xl font-bold">{stats.total_chunks}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Collection</Label>
                <p className="text-lg font-semibold">{stats.collection_name || "N/A"}</p>
              </div>
              <div>
                <Button variant="outline" onClick={loadStats} size="sm">
                  Refresh Stats
                </Button>
              </div>
            </div>
          ) : (
            <p className="text-muted-foreground">No statistics available</p>
          )}

          {stats && (
            <div className="mt-6 space-y-4">
              {Object.keys(stats.documents_by_language).length > 0 && (
                <div>
                  <Label className="text-muted-foreground mb-2 block">By Language</Label>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(stats.documents_by_language).map(([lang, count]) => (
                      <Badge key={lang} variant="secondary">
                        {lang}: {count} chunks
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {Object.keys(stats.documents_by_difficulty).length > 0 && (
                <div>
                  <Label className="text-muted-foreground mb-2 block">By Difficulty</Label>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(stats.documents_by_difficulty).map(([diff, count]) => (
                      <Badge key={diff} variant="outline">
                        {diff}: {count} chunks
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Query Card */}
      <Card>
        <CardHeader>
          <CardTitle>Query Vector Store</CardTitle>
          <CardDescription>
            Search for relevant content using semantic similarity. Results are retrieved from the
            vector database.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="query">Query</Label>
            <Textarea
              id="query"
              aria-label="RAG query input"
              placeholder="e.g., How do I create variables in Python?"
              value={query}
              onChange={e => setQuery(e.target.value)}
              rows={3}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="error-patterns">Error Patterns (Optional)</Label>
            <Textarea
              id="error-patterns"
              aria-label="Error patterns input"
              placeholder="Enter error patterns, one per line&#10;e.g., NameError: name 'x' is not defined"
              value={errorPatterns}
              onChange={e => setErrorPatterns(e.target.value)}
              rows={3}
            />
            <p className="text-sm text-muted-foreground">
              Error patterns help enhance the query for better relevance
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="top-k">Top K Results</Label>
            <Input
              id="top-k"
              aria-label="Top K results input"
              type="number"
              min={1}
              max={50}
              value={topK}
              onChange={e => setTopK(parseInt(e.target.value) || 5)}
            />
          </div>

          <Button onClick={handleQuery} disabled={isLoading || !query.trim()}>
            {isLoading ? (
              <>
                <LoadingSpinner className="mr-2" />
                Querying...
              </>
            ) : (
              "Query"
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Results Card */}
      {results && (
        <Card>
          <CardHeader>
            <CardTitle>Query Results</CardTitle>
            <CardDescription>
              Retrieved context from the vector database (Top {topK} results)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div
              className="whitespace-pre-wrap text-sm bg-muted p-4 rounded-md"
              role="region"
              aria-label="RAG query results"
            >
              {results}
            </div>
          </CardContent>
        </Card>
      )}

    </div>
  );
}
