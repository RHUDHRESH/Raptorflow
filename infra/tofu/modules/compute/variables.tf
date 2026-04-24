variable "name" { type = string }
variable "aws_region" { type = string }
variable "public_subnet_ids" { type = list(string) }
variable "private_subnet_ids" { type = list(string) }
variable "alb_security_group_id" { type = string }
variable "api_security_group_id" { type = string }
variable "qdrant_security_group_id" { type = string }
variable "certificate_arn" { type = string }
variable "image_uri" { type = string }
variable "qdrant_image_uri" { type = string }
variable "qdrant_efs_id" { type = string }
variable "database_app_secret_arn" { type = string }
variable "database_direct_secret_arn" { type = string }
variable "clerk_jwt_secret_arn" { type = string }
variable "bedrock_api_key_secret_arn" { type = string }
variable "razorpay_api_secret_arn" { type = string }
variable "resend_api_key_secret_arn" { type = string }
variable "execution_role_arn" { type = string }
variable "task_role_arn" { type = string }
variable "api_desired_count" {
  type    = number
  default = 2
}
variable "api_min_capacity" {
  type    = number
  default = 2
}
variable "api_max_capacity" {
  type    = number
  default = 10
}
variable "api_cpu_target_value" {
  type    = number
  default = 60
}
variable "api_deregistration_delay_seconds" {
  type    = number
  default = 30
}
variable "alb_idle_timeout_seconds" {
  type    = number
  default = 120
}
variable "qdrant_desired_count" {
  type    = number
  default = 1
}
variable "qdrant_cpu" {
  type    = number
  default = 1024
}
variable "qdrant_memory" {
  type    = number
  default = 2048
}
variable "qdrant_grpc_port" {
  type    = number
  default = 6334
}
variable "tags" { type = map(string) }


