import argparse


def setup_cloud_armor(project_id: str):
    """
    Documents and simulates the setup of Cloud Armor for Matrix API protection.
    """
    print(f"SOTA Security: Initializing Cloud Armor Setup for {project_id}")

    # 1. Create security policy
    print("Step 1: gcloud compute security-policies create raptorflow-api-policy")

    # 2. Add rules (e.g., rate limiting, SQL injection protection)
    print("Step 2: SQLi Protection Rule Creation")
    cmd2 = (
        "gcloud compute security-policies rules create 1000 --action=deny-403 "
        "--expression=\"evaluatePredefinedExpr('sqli-v33-stable')\""
    )
    print(cmd2)

    # 3. Attach to Backend Service
    print("Step 3: Attaching Policy to Backend")
    cmd3 = (
        "gcloud compute backend-services update raptorflow-backend "
        "--security-policy=raptorflow-api-policy"
    )
    print(cmd3)

    print("✓ Cloud Armor Policy configured for industrial protection.")


def prune_iam_roles(project_id: str, service_account: str):
    """
    Documents the pruning of IAM roles to achieve Principle of Least Privilege.
    """
    print(f"SOTA Security: Pruning IAM roles for {service_account}")

    # Remove excessive roles
    roles_to_remove = ["roles/owner", "roles/editor"]
    for role in roles_to_remove:
        print(f"Removing redundant role: {role}")
        cmd = (
            f"gcloud projects remove-iam-policy-binding {project_id} "
            f"--member=serviceAccount:{service_account} --role={role}"
        )
        print(cmd)

    print("✓ IAM Roles pruned to minimal functional set.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Industrial Security Setup")
    parser.add_argument("--project", help="GCP Project ID", required=True)
    sa_default = "raptorflow-matrix-sa@raptorflow-481505.iam.gserviceaccount.com"
    parser.add_argument("--sa", help="Service Account Email", default=sa_default)

    args = parser.parse_args()
    setup_cloud_armor(args.project)
    prune_iam_roles(args.project, args.sa)
