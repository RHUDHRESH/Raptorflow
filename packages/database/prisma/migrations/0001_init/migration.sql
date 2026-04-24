CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TYPE "OrgRole" AS ENUM ('owner', 'admin', 'member', 'viewer');

CREATE TABLE "organizations" (
    "orgId" UUID NOT NULL DEFAULT gen_random_uuid(),
    "name" TEXT NOT NULL,
    "slug" TEXT,
    "logo_url" TEXT,
    "plan_tier" TEXT DEFAULT 'free',
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "organizations_pkey" PRIMARY KEY ("orgId")
);

CREATE UNIQUE INDEX "organizations_slug_key" ON "organizations"("slug");

CREATE TABLE "users" (
    "clerk_user_id" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "first_name" TEXT,
    "last_name" TEXT,
    "avatar_url" TEXT,
    "referral_code" TEXT,
    "referral_applied_at" TIMESTAMP(3),
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "users_pkey" PRIMARY KEY ("clerk_user_id")
);

CREATE UNIQUE INDEX "users_email_key" ON "users"("email");

CREATE TABLE "org_members" (
    "org_member_id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "org_id" UUID NOT NULL,
    "clerk_user_id" TEXT NOT NULL,
    "role" "OrgRole" NOT NULL DEFAULT 'member',
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "org_members_pkey" PRIMARY KEY ("org_member_id")
);

CREATE UNIQUE INDEX "org_members_org_id_clerk_user_id_key" ON "org_members"("org_id", "clerk_user_id");

ALTER TABLE "org_members"
ADD CONSTRAINT "org_members_org_id_fkey"
FOREIGN KEY ("org_id") REFERENCES "organizations"("orgId")
ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "org_members"
ADD CONSTRAINT "org_members_user_id_fkey"
FOREIGN KEY ("clerk_user_id") REFERENCES "users"("clerk_user_id")
ON DELETE CASCADE ON UPDATE CASCADE;

CREATE TABLE "sessions" (
    "session_id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "org_id" UUID NOT NULL,
    "clerk_user_id" TEXT,
    "clerk_session_id" TEXT,
    "transport" TEXT NOT NULL DEFAULT 'http',
    "connected_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "disconnected_at" TIMESTAMP(3),
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "sessions_pkey" PRIMARY KEY ("session_id")
);

CREATE INDEX "sessions_org_id_idx" ON "sessions"("org_id");
CREATE INDEX "sessions_clerk_user_id_idx" ON "sessions"("clerk_user_id");
CREATE INDEX "sessions_clerk_session_id_idx" ON "sessions"("clerk_session_id");

ALTER TABLE "sessions"
ADD CONSTRAINT "sessions_org_id_fkey"
FOREIGN KEY ("org_id") REFERENCES "organizations"("orgId")
ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "sessions"
ADD CONSTRAINT "sessions_user_id_fkey"
FOREIGN KEY ("clerk_user_id") REFERENCES "users"("clerk_user_id")
ON DELETE SET NULL ON UPDATE CASCADE;
