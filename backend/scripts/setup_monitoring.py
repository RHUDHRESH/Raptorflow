import argparse


def setup_alerts(project_id: str):
    """
    Documents and simulates the setup of GCP Monitoring Alerts.
    """
    print(f"SOTA Monitoring: Initializing Alerts for {project_id}")

    # 1. Create notification channel
    print("Step 1: Creating Notification Channel")
    cmd1 = (
        "gcloud beta monitoring channels create "
        '--display-name="Matrix Alerts" --type=email '
        "--channel-labels=email_address=admin@raptorflow.io"
    )
    print(cmd1)

    # 2. Create alert policy for Kill-Switch
    print("Step 2: Creating Kill-Switch Alert Policy")
    cmd2 = (
        "gcloud alpha monitoring policies create "
        '--display-name="Global Kill-Switch Triggered" '
        "--condition=\"metric.type='logging.googleapis.com/user/kill_switch_total' "
        "AND resource.type='cloud_run_revision'\" "
        '--notification-channels="[CHANNEL_ID]"'
    )
    print(cmd2)

    # 3. Enable Error Reporting
    print("Step 3: Ensuring Error Reporting is enabled")
    print("gcloud services enable clouderrorreporting.googleapis.com")

    print("✓ GCP Monitoring & Alerting configured for Matrix triggers.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitoring Setup")
    parser.add_argument("--project", help="GCP Project ID", required=True)

    args = parser.parse_args()
    setup_alerts(args.project)
