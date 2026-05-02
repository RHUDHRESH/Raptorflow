use super::common::*;

pub async fn get_subscription_status(
    pool: &PgPool,
    org_id: uuid::Uuid,
) -> Result<String, sqlx::Error> {
    let row = sqlx::query(
        r#"
        SELECT status FROM subscriptions
        WHERE org_id = $1
        ORDER BY created_at DESC
        LIMIT 1
        "#,
    )
    .bind(org_id)
    .fetch_optional(pool)
    .await?;

    Ok(row
        .map(|r| r.get("status"))
        .unwrap_or_else(|| "none".to_string()))
}

pub async fn get_latest_subscription(
    pool: &PgPool,
    org_id: uuid::Uuid,
) -> Result<Option<Subscription>, sqlx::Error> {
    let row = sqlx::query_as::<_, Subscription>(
        r#"
        SELECT subscription_id, org_id, provider, status, plan_amount_inr,
               plan_tier, referral_code, discount_percent, grace_period_ends_at,
               created_at, updated_at
        FROM subscriptions
        WHERE org_id = $1
        ORDER BY created_at DESC
        LIMIT 1
        "#,
    )
    .bind(org_id)
    .fetch_optional(pool)
    .await?;

    Ok(row)
}

pub async fn create_subscription(
    pool: &PgPool,
    subscription_id: uuid::Uuid,
    org_id: uuid::Uuid,
    status: &str,
    plan_tier: &str,
    plan_amount_inr: i32,
    referral_code: Option<&str>,
    discount_percent: i32,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO subscriptions (
            subscription_id,
            org_id,
            provider,
            status,
            plan_amount_inr,
            plan_tier,
            referral_code,
            discount_percent
        )
        VALUES ($1, $2, 'referral', $3, $4, $5, $6, $7)
        ON CONFLICT (subscription_id) DO UPDATE SET
            status = EXCLUDED.status,
            plan_amount_inr = EXCLUDED.plan_amount_inr,
            plan_tier = EXCLUDED.plan_tier,
            referral_code = EXCLUDED.referral_code,
            discount_percent = EXCLUDED.discount_percent,
            updated_at = NOW()
        "#,
    )
    .bind(subscription_id)
    .bind(org_id)
    .bind(status)
    .bind(plan_amount_inr)
    .bind(plan_tier)
    .bind(referral_code)
    .bind(discount_percent)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn update_subscription_status(
    pool: &PgPool,
    subscription_id: &str,
    status: &str,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        UPDATE subscriptions
        SET status = $1, updated_at = NOW()
        WHERE subscription_id::text = $2
        "#,
    )
    .bind(status)
    .bind(subscription_id)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn get_subscription_by_razorpay_id(
    pool: &PgPool,
    org_id: uuid::Uuid,
    subscription_id_str: &str,
) -> Result<Option<Subscription>, sqlx::Error> {
    let row = sqlx::query_as::<_, Subscription>(
        r#"
        SELECT subscription_id, org_id, provider, status, plan_amount_inr,
               plan_tier, referral_code, discount_percent, grace_period_ends_at,
               created_at, updated_at
        FROM subscriptions
        WHERE org_id = $1 AND subscription_id::text = $2
        "#,
    )
    .bind(org_id)
    .bind(subscription_id_str)
    .fetch_optional(pool)
    .await?;

    Ok(row)
}

pub async fn upsert_referral_subscription(
    pool: &PgPool,
    org_id: uuid::Uuid,
    plan_tier: &str,
    referral_code: &str,
) -> Result<(), sqlx::Error> {
    let subscription_id = uuid::Uuid::new_v4();

    create_subscription(
        pool,
        subscription_id,
        org_id,
        "active",
        plan_tier,
        0,
        Some(referral_code),
        100,
    )
    .await
}

pub async fn get_user_referral_code(
    pool: &PgPool,
    clerk_user_id: &str,
) -> Result<Option<String>, sqlx::Error> {
    let row = sqlx::query(
        r#"
        SELECT referral_code
        FROM users
        WHERE clerk_user_id = $1
        ORDER BY updated_at DESC
        LIMIT 1
        "#,
    )
    .bind(clerk_user_id)
    .fetch_optional(pool)
    .await?;

    Ok(row.and_then(|row| {
        row.try_get::<Option<String>, _>("referral_code")
            .ok()
            .flatten()
    }))
}

pub async fn create_payment_event(
    pool: &PgPool,
    event_id: uuid::Uuid,
    org_id: uuid::Uuid,
    razorpay_event_id: &str,
    event_type: &str,
    payment_id: Option<&str>,
    order_id: Option<&str>,
    amount: Option<i64>,
    currency: Option<&str>,
    status: Option<&str>,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO payment_events (event_id, org_id, razorpay_event_id, event_type, payment_id, order_id, amount, currency, status)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        ON CONFLICT (razorpay_event_id) DO NOTHING
        "#,
    )
    .bind(event_id)
    .bind(org_id)
    .bind(razorpay_event_id)
    .bind(event_type)
    .bind(payment_id)
    .bind(order_id)
    .bind(amount)
    .bind(currency)
    .bind(status)
    .execute(pool)
    .await?;
    Ok(())
}
