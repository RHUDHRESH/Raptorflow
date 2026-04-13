variable "name" { type = string }
variable "private_subnet_ids" { type = list(string) }
variable "database_subnet_ids" { type = list(string) }
variable "db_security_group_id" { type = string }
variable "dragonfly_security_group_id" { type = string }
variable "qdrant_security_group_id" { type = string }
variable "db_name" { type = string }
variable "db_username" { type = string }
variable "dragonfly_ami_id" {
  type = string

  validation {
    condition     = startswith(var.dragonfly_ami_id, "ami-") && var.dragonfly_ami_id != "ami-0123456789abcdef0"
    error_message = "Provide a real private AMI ID for Dragonfly rather than the scaffold placeholder."
  }
}
variable "tags" { type = map(string) }
