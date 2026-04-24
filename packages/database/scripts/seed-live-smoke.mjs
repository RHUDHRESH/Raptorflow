import { randomUUID } from "node:crypto";
import { createHash } from "node:crypto";
import { Client } from "pg";

function requireEnv(name, fallback = undefined) {
  const value = process.env[name] ?? fallback;
  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return value;
}

function normalizeRole(role) {
  const value = String(role ?? "").toLowerCase();
  if (value.includes("owner")) return "owner";
  if (value.includes("admin")) return "admin";
  if (value.includes("viewer")) return "viewer";
  return "member";
}

async function withPg(url, fn) {
  const client = new Client({ connectionString: url });
  await client.connect();
  try {
    return await fn(client);
  } finally {
    await client.end().catch(() => {});
  }
}

async function seedPrismaDb({ userId, email, orgId }) {
  const databaseUrl = requireEnv(
    "DATABASE_URL",
    process.env.RAPTORFLOW_DATABASE_URL ??
      process.env.DIRECT_DATABASE_URL ??
      process.env.RAPTORFLOW_DIRECT_DATABASE_URL,
  );

  await withPg(databaseUrl, async (client) => {
    await client.query(
      `CREATE TABLE IF NOT EXISTS generated_content (
         content_id TEXT PRIMARY KEY,
         org_id UUID NOT NULL,
         campaign_id TEXT,
         task_id TEXT,
         content_type TEXT NOT NULL,
         status TEXT NOT NULL,
         body JSONB NOT NULL,
         created_at TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP
       )`,
    );

    await client.query(
      `CREATE INDEX IF NOT EXISTS generated_content_org_id_idx
       ON generated_content (org_id)`,
    );

    await client.query(
      `INSERT INTO users (clerk_user_id, email, first_name, last_name, created_at, updated_at)
       VALUES ($1, $2, 'Live', 'Smoke', NOW(), NOW())
       ON CONFLICT (clerk_user_id) DO UPDATE SET
         email = EXCLUDED.email,
         first_name = EXCLUDED.first_name,
         last_name = EXCLUDED.last_name,
         updated_at = EXCLUDED.updated_at`,
      [userId, email],
    );

    await client.query(
      `INSERT INTO campaigns (id, clerk_user_id, title, brief, status, goal, budget, timeframe, evaluation_result, evaluated_at, "createdAt", "updatedAt")
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NULL, NULL, NOW(), NOW())
       ON CONFLICT (id) DO UPDATE SET
         title = EXCLUDED.title,
         brief = EXCLUDED.brief,
         status = EXCLUDED.status,
         goal = EXCLUDED.goal,
         budget = EXCLUDED.budget,
         timeframe = EXCLUDED.timeframe,
         "updatedAt" = EXCLUDED."updatedAt"`,
      [
        "live-smoke-campaign",
        userId,
        "Live Smoke Campaign",
        "Live smoke seeded campaign for end-to-end verification.",
        "active",
        "re_engagement",
        "organic",
        "30 days",
      ],
    );

    await client.query(
      `INSERT INTO council_sessions (id, clerk_user_id, topic, context, status, error_message, last_scan_result, "synthesisResult", "synthesizedAt", "createdAt", "updatedAt")
       VALUES ($1, $2, $3, $4, $5, NULL, NULL, NULL, NULL, NOW(), NOW())
       ON CONFLICT (id) DO UPDATE SET
         topic = EXCLUDED.topic,
         context = EXCLUDED.context,
         status = EXCLUDED.status,
         "updatedAt" = EXCLUDED."updatedAt"`,
      [
        "01KPB8VE4DE9XJEBNRYQ15J8TV",
        userId,
        "live-smoke-campaign",
        "Review the live smoke campaign and confirm it is healthy.",
        "completed",
      ],
    );

    await client.query(
      `INSERT INTO muse_conversations (id, clerk_user_id, title, "createdAt", "updatedAt")
       VALUES ($1, $2, $3, NOW(), NOW())
       ON CONFLICT (id) DO UPDATE SET
         title = EXCLUDED.title,
         "updatedAt" = EXCLUDED."updatedAt"`,
      ["live-smoke-muse-conversation", userId, "New conversation"],
    );

    await client.query(
      `INSERT INTO muse_messages (id, conversation_id, role, content, route, "createdAt")
       VALUES ($1, $2, $3, $4, $5, NOW())
       ON CONFLICT (id) DO UPDATE SET
         role = EXCLUDED.role,
         content = EXCLUDED.content,
         route = EXCLUDED.route`,
      [
        "live-smoke-muse-message",
        "live-smoke-muse-conversation",
        "assistant",
        "strategic",
        "strategic",
      ],
    );

    if (orgId) {
      await client.query(
        `INSERT INTO organizations ("orgId", name, slug, created_at, updated_at)
         VALUES ($1::uuid, $2, $3, NOW(), NOW())
         ON CONFLICT ("orgId") DO UPDATE SET
           name = EXCLUDED.name,
           slug = EXCLUDED.slug,
           updated_at = EXCLUDED.updated_at`,
        [orgId, "Live Smoke Org", "live-smoke-org"],
      );

      await client.query(
        `INSERT INTO org_members ("orgMemberId", org_id, clerk_user_id, role, created_at, updated_at)
         VALUES ($1::uuid, $2::uuid, $3, $4, NOW(), NOW())
         ON CONFLICT (org_id, clerk_user_id) DO UPDATE SET
           role = EXCLUDED.role,
           updated_at = EXCLUDED.updated_at`,
        [randomUUID(), orgId, userId, "owner"],
      );

      await client.query(
        `INSERT INTO sessions (session_id, org_id, clerk_user_id, clerk_session_id, transport, connected_at, created_at, updated_at)
         VALUES ($1::uuid, $2::uuid, $3, $4, 'e2e', NOW(), NOW(), NOW())
         ON CONFLICT (session_id) DO UPDATE SET
           org_id = EXCLUDED.org_id,
           clerk_user_id = EXCLUDED.clerk_user_id,
           clerk_session_id = EXCLUDED.clerk_session_id,
           transport = EXCLUDED.transport,
           updated_at = EXCLUDED.updated_at`,
        [randomUUID(), orgId, userId, null],
      );

      await client.query(
        `INSERT INTO generated_content (content_id, org_id, campaign_id, task_id, content_type, status, body, created_at)
         VALUES ($1, $2::uuid, $3, NULL, $4, $5, $6::jsonb, NOW())
         ON CONFLICT (content_id) DO UPDATE SET
           body = EXCLUDED.body,
           status = EXCLUDED.status`,
        [
          "live-smoke-generated-content",
          orgId,
          "live-smoke-campaign",
          "social_post",
          "published",
          JSON.stringify({
            headline: "Live Smoke Post",
            title: "Live Smoke Post",
            body: "Persisted content used to verify the production data pipeline.",
          }),
        ],
      );
    }
  });
}

async function seedRustDb({ userId, email, orgId, orgRole, clerkSessionId }) {
  const normalizedRole = normalizeRole(orgRole);

  await withPg(
    requireEnv(
      "RAPTORFLOW_LOCAL_DATABASE_URL",
      "postgres://raptorflow:raptorflow@localhost:6432/raptorflow",
    ),
    async (client) => {
      await client.query(
        `INSERT INTO organizations (org_id, name, subscription_status, foundation_version, created_at, updated_at)
         VALUES ($1::uuid, $2, 'none', 0, NOW(), NOW())
         ON CONFLICT (org_id) DO UPDATE SET name = EXCLUDED.name, updated_at = EXCLUDED.updated_at`,
        [orgId, "Live Smoke Org"],
      );

      await client.query(
        `INSERT INTO users (clerk_user_id, email, first_name, last_name, created_at, updated_at)
         VALUES ($1, $2, 'Live', 'Smoke', NOW(), NOW())
         ON CONFLICT (clerk_user_id) DO UPDATE SET email = EXCLUDED.email, updated_at = EXCLUDED.updated_at`,
        [userId, email],
      );

      await client.query(
        `INSERT INTO org_users (org_user_id, org_id, clerk_user_id, email, role, created_at)
         VALUES ($1::uuid, $2::uuid, $3, $4, $5, NOW())
         ON CONFLICT (org_id, clerk_user_id) DO UPDATE SET email = EXCLUDED.email, role = EXCLUDED.role`,
        [randomUUID(), orgId, userId, email, normalizedRole],
      );

      await client.query(
        `INSERT INTO org_members (member_id, org_id, user_id, role, created_at, updated_at)
         VALUES ($1::uuid, $2::uuid, $3, $4, NOW(), NOW())
         ON CONFLICT (org_id, user_id) DO UPDATE SET role = EXCLUDED.role, updated_at = EXCLUDED.updated_at`,
        [randomUUID(), orgId, userId, normalizedRole],
      );

      await client.query(
        `INSERT INTO sessions (session_id, org_id, user_id, socket_id, status, metadata, last_seen_at, created_at, updated_at)
         VALUES ($1::uuid, $2::uuid, $3, $4, 'active', '{}'::jsonb, NOW(), NOW(), NOW())
         ON CONFLICT (session_id) DO UPDATE SET
           user_id = EXCLUDED.user_id,
           socket_id = EXCLUDED.socket_id,
           status = EXCLUDED.status,
           metadata = EXCLUDED.metadata,
           last_seen_at = EXCLUDED.last_seen_at,
           updated_at = EXCLUDED.updated_at`,
        [randomUUID(), orgId, userId, clerkSessionId || null],
      );

      await client.query(
        `INSERT INTO campaigns (campaign_id, org_id, name, goal, status, active_move_id, created_at, updated_at)
         VALUES ($1, $2::uuid, $3, $4, $5, $6, NOW(), NOW())
         ON CONFLICT (campaign_id) DO UPDATE SET name = EXCLUDED.name, goal = EXCLUDED.goal, status = EXCLUDED.status, active_move_id = EXCLUDED.active_move_id, updated_at = EXCLUDED.updated_at`,
        [
          "live-smoke-campaign",
          orgId,
          "Live Smoke Campaign",
          "re_engagement",
          "active",
          "live-smoke-campaign-move",
        ],
      );

      await client.query(
        `INSERT INTO campaign_moves (move_id, campaign_id, org_id, move_type, sequence_number, status, created_at)
         VALUES ($1, $2, $3::uuid, $4, 1, 'planned', NOW())
         ON CONFLICT (move_id) DO UPDATE SET status = EXCLUDED.status`,
        ["live-smoke-campaign-move", "live-smoke-campaign", orgId, "strategic"],
      );

      await client.query(
        `INSERT INTO campaign_tasks (task_id, move_id, campaign_id, org_id, title, status, scheduled_date, created_at)
         VALUES ($1, $2, $3, $4::uuid, $5, 'pending', CURRENT_DATE, NOW())
         ON CONFLICT (task_id) DO UPDATE SET title = EXCLUDED.title`,
        ["live-smoke-campaign-task", "live-smoke-campaign-move", "live-smoke-campaign", orgId, "Smoke Task"],
      );

      await client.query(
        `INSERT INTO council_sessions (session_id, org_id, campaign_id, session_type, status, question, total_cost_usd, created_at)
         VALUES ($1, $2::uuid, $3, $4, 'completed', $5, 0, NOW())
         ON CONFLICT (session_id) DO UPDATE SET status = EXCLUDED.status, question = EXCLUDED.question`,
        [
          "01KPB8VE4DE9XJEBNRYQ15J8TV",
          orgId,
          "live-smoke-campaign",
          "strategic_review",
          "Review the live smoke campaign and confirm it is healthy.",
        ],
      );

      await client.query(
        `INSERT INTO muse_conversations (conversation_id, org_id, route, created_at)
         VALUES ($1, $2::uuid, $3, NOW())
         ON CONFLICT (conversation_id) DO UPDATE SET route = EXCLUDED.route`,
        ["live-smoke-muse-conversation", orgId, "strategic"],
      );

      await client.query(
        `INSERT INTO muse_messages (message_id, conversation_id, org_id, role, body, created_at)
         VALUES ($1, $2, $3::uuid, $4, $5, NOW())
         ON CONFLICT (message_id) DO UPDATE SET body = EXCLUDED.body, role = EXCLUDED.role`,
        [
          "live-smoke-muse-message",
          "live-smoke-muse-conversation",
          orgId,
          "assistant",
          "strategic",
        ],
      );

      await client.query(
        `INSERT INTO generated_content (content_id, org_id, campaign_id, task_id, content_type, status, body, created_at)
         VALUES ($1, $2::uuid, $3, NULL, $4, $5, $6::jsonb, NOW())
         ON CONFLICT (content_id) DO UPDATE SET body = EXCLUDED.body, status = EXCLUDED.status`,
        [
          "live-smoke-generated-content",
          orgId,
          "live-smoke-campaign",
          "social_post",
          "published",
          JSON.stringify({
            headline: "Live Smoke Post",
            title: "Live Smoke Post",
            body: "Persisted content used to verify the production data pipeline.",
          }),
        ],
      );
    },
  );
}

async function main() {
  const userId = requireEnv("LIVE_SMOKE_USER_ID");
  const email = requireEnv("LIVE_SMOKE_USER_EMAIL");
  const clerkOrgId = process.env.LIVE_SMOKE_ORGANIZATION_ID ?? "";
  const orgId = process.env.LIVE_SMOKE_ORG_ID ?? "";
  const orgRole = process.env.LIVE_SMOKE_ORG_ROLE ?? "owner";
  const clerkSessionId = process.env.LIVE_SMOKE_SESSION_ID ?? "";

  if (clerkOrgId && !clerkOrgId.startsWith("org_")) {
    throw new Error(
      `LIVE_SMOKE_ORGANIZATION_ID must be a Clerk org id if provided, received: ${clerkOrgId}`,
    );
  }

  const resolvedOrgId = orgId || (clerkOrgId ? deriveInternalOrgId(clerkOrgId) : "");

  if (resolvedOrgId && !/^[0-9a-fA-F-]{36}$/.test(resolvedOrgId)) {
    throw new Error(
      `LIVE_SMOKE_ORG_ID must be a UUID if provided, received: ${resolvedOrgId}`,
    );
  }

  await seedPrismaDb({ userId, email, orgId: resolvedOrgId || undefined });
  if (resolvedOrgId) {
    await seedRustDb({
      userId,
      email,
      orgId: resolvedOrgId,
      orgRole,
      clerkSessionId: clerkSessionId || null,
    });
  }

  console.log("seeded live smoke data");
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});

function deriveInternalOrgId(clerkOrgId) {
  const digest = createHash("sha256")
    .update("raptorflow-clerk-org:")
    .update(clerkOrgId)
    .digest();
  const bytes = Buffer.from(digest.subarray(0, 16));
  bytes[6] = (bytes[6] & 0x0f) | 0x50;
  bytes[8] = (bytes[8] & 0x3f) | 0x80;
  const hex = bytes.toString("hex");
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(
    16,
    20,
  )}-${hex.slice(20, 32)}`;
}
