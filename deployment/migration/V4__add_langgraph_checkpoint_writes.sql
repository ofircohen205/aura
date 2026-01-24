-- LangGraph Postgres checkpointer tables (writes)
--
-- The langgraph-checkpoint-postgres implementation expects a `checkpoint_writes` table.
-- Earlier migrations only created `checkpoints` and `checkpoint_blobs`, which causes runtime
-- errors when workflows attempt to persist/read pending writes.

CREATE TABLE IF NOT EXISTS checkpoint_writes (
    thread_id TEXT NOT NULL,
    checkpoint_ns TEXT NOT NULL DEFAULT '',
    checkpoint_id TEXT NOT NULL,
    task_id TEXT NOT NULL,
    task_path TEXT NOT NULL DEFAULT '',
    idx INTEGER NOT NULL,
    channel TEXT NOT NULL,
    type TEXT,
    blob BYTEA NOT NULL,
    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id, task_id, idx)
);

CREATE INDEX IF NOT EXISTS checkpoint_writes_thread_id_idx
    ON checkpoint_writes(thread_id);
