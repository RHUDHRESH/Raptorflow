module "stack" {
  source = "../dev"

  aws_region              = var.aws_region
  name                    = var.name
  allowed_cidr            = var.allowed_cidr
  github_oidc_thumbprints  = var.github_oidc_thumbprints
  certificate_arn         = var.certificate_arn
  image_uri               = var.image_uri
  qdrant_image_uri        = var.qdrant_image_uri
  dragonfly_ami_id        = var.dragonfly_ami_id
  execution_role_arn      = var.execution_role_arn
  task_role_arn           = var.task_role_arn
}
