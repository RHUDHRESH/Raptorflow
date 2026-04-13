variable "aws_region" { type = string default = "ap-south-1" }
variable "name" { type = string default = "raptorflow-prod" }
variable "allowed_cidr" { type = string default = "0.0.0.0/0" }
variable "github_oidc_thumbprints" {
  type = list(string)
  default = ["REPLACE_WITH_REAL_GITHUB_OIDC_THUMBPRINT"]
}
variable "certificate_arn" { type = string default = "arn:aws:acm:ap-south-1:123456789012:certificate/prod" }
variable "image_uri" { type = string default = "123456789012.dkr.ecr.ap-south-1.amazonaws.com/raptorflow-api:prod" }
variable "qdrant_image_uri" { type = string default = "qdrant/qdrant:latest" }
variable "dragonfly_ami_id" { type = string default = "ami-REPLACE_WITH_HARDENED_DRAGONFLY_AMI" }
variable "execution_role_arn" { type = string default = "arn:aws:iam::123456789012:role/raptorflow-prod-execution" }
variable "task_role_arn" { type = string default = "arn:aws:iam::123456789012:role/raptorflow-prod-task" }
