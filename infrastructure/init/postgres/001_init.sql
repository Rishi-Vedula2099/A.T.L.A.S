-- ==============================================================================
-- A.T.L.A.S — PostgreSQL schema initialization
-- Mounted into /docker-entrypoint-initdb.d/ — runs once on a fresh volume.
-- ==============================================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;  -- for gen_random_uuid()

-- --- Users --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    display_name  TEXT,
    role          TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('user','admin')),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- --- Refresh tokens (rotation + revocation) -----------------------------------
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    jti        TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked    BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user ON refresh_tokens(user_id);

-- --- Session messages (used by services/memory.py) ----------------------------
CREATE TABLE IF NOT EXISTS session_messages (
    id          BIGSERIAL PRIMARY KEY,
    session_id  TEXT NOT NULL,
    role        TEXT NOT NULL CHECK (role IN ('user','assistant','system')),
    content     TEXT NOT NULL,
    metadata    JSONB,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_session_messages_session ON session_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_session_messages_created ON session_messages(created_at DESC);

-- --- Updated_at trigger -------------------------------------------------------
CREATE OR REPLACE FUNCTION touch_updated_at() RETURNS trigger AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_users_touch ON users;
CREATE TRIGGER trg_users_touch BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION touch_updated_at();

-- --- Bootstrap admin (only if env vars are set) ------------------------------
-- The installer writes ATLAS_BOOTSTRAP_ADMIN_EMAIL / _PASSWORD into the .env
-- passed to the postgres container; pgcrypto-based hashing happens at app boot.
DO $$
BEGIN
    IF current_setting('app.bootstrap_admin_email', true) IS NOT NULL
       AND current_setting('app.bootstrap_admin_email', true) <> ''
       AND current_setting('app.bootstrap_admin_password', true) IS NOT NULL
       AND current_setting('app.bootstrap_admin_password', true) <> ''
    THEN
        INSERT INTO users (email, password_hash, role, display_name)
        VALUES (
            current_setting('app.bootstrap_admin_email', true),
            -- Stored as plaintext sentinel; the backend re-hashes on first login.
            -- For real bootstrap, run scripts/seed_admin.py instead.
            'BOOTSTRAP:' || current_setting('app.bootstrap_admin_password', true),
            'admin',
            'ATLAS Admin'
        )
        ON CONFLICT (email) DO NOTHING;
        RAISE NOTICE 'Bootstrap admin ensured for %', current_setting('app.bootstrap_admin_email', true);
    END IF;
END $$;
