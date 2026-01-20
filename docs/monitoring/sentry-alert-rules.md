# Sentry Alert Rules Configuration

## Overview
This document outlines the configured alert rules for RaptorFlow in Sentry. These rules ensure that the team is notified of critical issues while maintaining zero-noise for routine development activities.

## 1. Production Critical Errors
**Trigger:** Any new issue in the `production` environment with a severity of `error` or higher.
**Actions:**
- Send Slack notification to `#alerts-production`.
- Send email to `engineering-oncall@raptorflow.com`.
**Filter:** `environment:production level:error`

## 2. High Frequency Backend Errors
**Trigger:** An issue is seen more than 50 times in 1 hour.
**Actions:**
- Send Slack notification to `#alerts-backend`.
**Filter:** `service:raptorflow-backend`

## 3. AI Inference Performance Regressions
**Trigger:** The duration of the `titan.research` or `blackbox.strategy` transaction exceeds 30 seconds for 10% of users in a 15-minute window.
**Actions:**
- Send Slack notification to `#alerts-performance`.
**Filter:** `transaction.duration:>30s`

## 4. Development Filter (Noise Reduction)
**Strategy:** All issues in the `development` environment are captured but do not trigger Slack or Email alerts.
**Enforcement:** Alert rules must include `environment:production` or `environment:preview` to be active for notifications.
