variable "aws_region" { type = string default = "ap-south-1" }
variable "name" { type = string default = "raptorflow-staging" }
variable "allowed_cidr" { type = string default = "0.0.0.0/0" }
variable "github_oidc_thumbprints" {
  type = list(string)
  default = ["REPLACE_WITH_REAL_GITHUB_OIDC_THUMBPRINT"]
}
variable "certificate_arn" { type = string default = "arn:aws:acm:ap-south-1:123456789012:certificate/staging" }
variable "image_uri" { type = string default = "123456789012.dkr.ecr.ap-south-1.amazonaws.com/raptorflow-api:staging" }
variable "qdrant_image_uri" { type = string default = "qdrant/qdrant:latest" }
variable "vector_node_ami_id" { type = string default = "ami-REPLACE_WITH_HARDENED_VECTOR_AMI" }
variable "execution_role_arn" { type = string default = "arn:aws:iam::123456789012:role/raptorflow-staging-execution" }
variable "task_role_arn" { type = string default = "arn:aws:iam::123456789012:role/raptorflow-staging-task" }


