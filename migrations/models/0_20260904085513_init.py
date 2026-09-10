from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "cities" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL
);
COMMENT ON TABLE "cities" IS 'Справочник городов';
CREATE TABLE IF NOT EXISTS "users" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "first_name" VARCHAR(255) NOT NULL,
    "last_name" VARCHAR(255) NOT NULL,
    "other_name" VARCHAR(255),
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "phone" VARCHAR(32),
    "birthday" DATE,
    "additional_info" TEXT,
    "is_admin" BOOL NOT NULL DEFAULT False,
    "password_hash" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "city_id" INT REFERENCES "cities" ("id") ON DELETE SET NULL
);
COMMENT ON TABLE "users" IS 'Основная модель пользователя';
CREATE TABLE IF NOT EXISTS "sessions" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "token_hash" VARCHAR(64) NOT NULL UNIQUE,
    "expires_at" TIMESTAMPTZ NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_sessions_token_h_bec082" ON "sessions" ("token_hash");
CREATE INDEX IF NOT EXISTS "idx_sessions_expires_6bcc94" ON "sessions" ("expires_at");
COMMENT ON TABLE "sessions" IS 'Отзываемая серверная сессия';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
