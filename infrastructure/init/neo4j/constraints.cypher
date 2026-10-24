// ==============================================================================
// A.T.L.A.S — Neo4j constraints + indexes
// Run once on a fresh database. Safe to re-run (IF NOT EXISTS).
// ==============================================================================

// Uniqueness constraints
CREATE CONSTRAINT user_email_unique IF NOT EXISTS
FOR (u:User) REQUIRE u.email IS UNIQUE;

CREATE CONSTRAINT user_id_unique IF NOT EXISTS
FOR (u:User) REQUIRE u.id IS UNIQUE;

// Existence constraints (required properties)
CREATE CONSTRAINT user_id_exists IF NOT EXISTS
FOR (u:User) REQUIRE u.id IS NOT NULL;

// Range indexes for fast lookups
CREATE INDEX user_created_at_index IF NOT EXISTS
FOR (u:User) ON (u.created_at);

CREATE INDEX technology_name_index IF NOT EXISTS
FOR (t:Technology) ON (t.name);

// Full-text index for searching memory text
CREATE FULLTEXT INDEX memory_search_index IF NOT EXISTS
FOR (m:Memory) ON EACH [m.text, m.summary];
