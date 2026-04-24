locals {
  tags = {
    project     = "raptorflow"
    environment = "dev"
    managed_by  = "tofu"
  }
}

module "network" {
  source                = "../../modules/network"
  name                  = var.name
  vpc_cidr              = "10.20.0.0/16"
  availability_zones    = ["ap-south-1a", "ap-south-1b", "ap-south-1c"]
  public_subnet_cidrs   = ["10.20.0.0/24", "10.20.1.0/24", "10.20.2.0/24"]
  private_subnet_cidrs  = ["10.20.10.0/24", "10.20.11.0/24", "10.20.12.0/24"]
  database_subnet_cidrs = ["10.20.20.0/24", "10.20.21.0/24", "10.20.22.0/24"]
  tags                  = local.tags
}

module "security" {
  source                = "../../modules/security"
  name                  = var.name
  vpc_id                = module.network.vpc_id
  allowed_cidr          = var.allowed_cidr
  github_org            = "raptorflow"
  github_repo           = "raptorflow"
  github_oidc_thumbprints = var.github_oidc_thumbprints
  tags                  = local.tags
}

module "data" {
  source                      = "../../modules/data"
  name                        = var.name
  private_subnet_ids          = module.network.private_subnet_ids
  database_subnet_ids         = module.network.database_subnet_ids
  db_security_group_id        = module.security.db_security_group_id
  vector_security_group_id = module.security.vector_security_group_id
  qdrant_security_group_id    = module.security.qdrant_security_group_id
  db_name                     = "raptorflow"
  db_username                 = "raptorflow"
  vector_node_ami_id            = var.vector_node_ami_id
  tags                        = local.tags
}

module "compute" {
  source                        = "../../modules/compute"
  name                          = var.name
  aws_region                    = var.aws_region
  public_subnet_ids             = module.network.public_subnet_ids
  private_subnet_ids            = module.network.private_subnet_ids
  alb_security_group_id         = module.security.alb_security_group_id
  api_security_group_id         = module.security.api_security_group_id
  qdrant_security_group_id      = module.security.qdrant_security_group_id
  certificate_arn               = var.certificate_arn
  image_uri                     = var.image_uri
  qdrant_image_uri              = var.qdrant_image_uri
  qdrant_efs_id                 = module.data.qdrant_efs_id
  database_app_secret_arn       = module.security.database_app_secret_arn
  database_direct_secret_arn    = module.security.database_direct_secret_arn
  clerk_jwt_secret_arn          = module.security.clerk_jwt_secret_arn
  bedrock_api_key_secret_arn        = module.security.bedrock_api_key_secret_arn
  razorpay_api_secret_arn       = module.security.razorpay_api_secret_arn
  resend_api_key_secret_arn     = module.security.resend_api_key_secret_arn
  execution_role_arn            = var.execution_role_arn
  task_role_arn                 = var.task_role_arn
  tags                          = local.tags
}

module "observability" {
  source               = "../../modules/observability"
  name                 = var.name
  cluster_name         = module.compute.cluster_name
  load_balancer_dns_name = module.compute.load_balancer_dns_name
  tags                 = local.tags
}

module "vercel" {
  source         = "../../modules/vercel"
  project_name   = "raptorflow-web-dev"
  root_directory = "apps/web"
}

