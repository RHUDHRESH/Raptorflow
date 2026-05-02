use super::common::*;

pub async fn get_organizations(pool: &PgPool) -> Result<Vec<Organization>, sqlx::Error> {
    let rows = sqlx::query(
        r#"
        SELECT org_id, name, subscription_status, foundation_version,
               foundation_complete, foundation_json, foundation_completed_at,
               created_at, updated_at
        FROM organizations
        WHERE org_id = app.current_org_id()
        "#,
    )
    .fetch_all(pool)
    .await?;

    rows.iter()
        .map(|row| {
            Ok(Organization {
                org_id: row.get("org_id"),
                name: row.get("name"),
                subscription_status: row.get("subscription_status"),
                foundation_version: row.get("foundation_version"),
                foundation_complete: row.get("foundation_complete"),
                foundation_json: row.get("foundation_json"),
                foundation_completed_at: row.get("foundation_completed_at"),
                created_at: row.get("created_at"),
                updated_at: row.get("updated_at"),
            })
        })
        .collect()
}

pub async fn get_org_users(pool: &PgPool) -> Result<Vec<OrgUser>, sqlx::Error> {
    let rows = sqlx::query(
        r#"
        SELECT org_user_id, org_id, clerk_user_id, email, role, created_at
        FROM org_users
        WHERE org_id = app.current_org_id()
        "#,
    )
    .fetch_all(pool)
    .await?;

    rows.iter()
        .map(|row| {
            Ok(OrgUser {
                org_user_id: row.get("org_user_id"),
                org_id: row.get("org_id"),
                clerk_user_id: row.get("clerk_user_id"),
                email: row.get("email"),
                role: row.get("role"),
                created_at: row.get("created_at"),
            })
        })
        .collect()
}

pub async fn create_organization(
    pool: &PgPool,
    org_id: uuid::Uuid,
    name: &str,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO organizations (org_id, name)
        VALUES ($1, $2)
        ON CONFLICT (org_id) DO UPDATE SET name = EXCLUDED.name
        "#,
    )
    .bind(org_id)
    .bind(name)
    .execute(pool)
    .await?;

    Ok(())
}

pub async fn create_org_user(
    pool: &PgPool,
    org_user_id: uuid::Uuid,
    org_id: uuid::Uuid,
    clerk_user_id: &str,
    email: &str,
    role: &str,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO org_users (org_user_id, org_id, clerk_user_id, email, role)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (org_id, clerk_user_id) DO UPDATE SET email = EXCLUDED.email
        "#,
    )
    .bind(org_user_id)
    .bind(org_id)
    .bind(clerk_user_id)
    .bind(email)
    .bind(role)
    .execute(pool)
    .await?;

    sqlx::query(
        r#"
        INSERT INTO org_members (member_id, org_id, user_id, role)
        VALUES ($1, $2, $3, $4::org_member_role)
        ON CONFLICT (org_id, user_id) DO UPDATE SET
            role = EXCLUDED.role,
            updated_at = NOW()
        "#,
    )
    .bind(uuid::Uuid::new_v4())
    .bind(org_id)
    .bind(clerk_user_id)
    .bind(role)
    .execute(pool)
    .await?;

    Ok(())
}

pub async fn get_foundation_snapshots(
    pool: &PgPool,
    org_id: uuid::Uuid,
) -> Result<Vec<FoundationSnapshot>, sqlx::Error> {
    let rows = sqlx::query(
        r#"
        SELECT foundation_snapshot_id, org_id, foundation_version, sections, source, created_at, updated_at
        FROM foundation_snapshots
        WHERE org_id = $1
        ORDER BY foundation_version DESC
        "#,
    )
    .bind(org_id)
    .fetch_all(pool)
    .await?;

    rows.iter()
        .map(|row| {
            Ok(FoundationSnapshot {
                foundation_snapshot_id: row.get("foundation_snapshot_id"),
                org_id: row.get("org_id"),
                foundation_version: row.get("foundation_version"),
                sections: row.get("sections"),
                source: row.get("source"),
                created_at: row.get("created_at"),
                updated_at: row.get("updated_at"),
            })
        })
        .collect()
}

pub async fn create_foundation_snapshot(
    pool: &PgPool,
    snapshot_id: &str,
    org_id: uuid::Uuid,
    version: i32,
    sections: &serde_json::Value,
    source: &str,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO foundation_snapshots (foundation_snapshot_id, org_id, foundation_version, sections, source)
        VALUES ($1, $2, $3, $4, $5)
        "#,
    )
    .bind(snapshot_id)
    .bind(org_id)
    .bind(version)
    .bind(sections)
    .bind(source)
    .execute(pool)
    .await?;
    Ok(())
}
