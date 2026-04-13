variable "name" { type = string }
variable "vpc_id" { type = string }
variable "allowed_cidr" { type = string }
variable "github_org" { type = string }
variable "github_repo" { type = string }
variable "github_oidc_thumbprints" {
  type = list(string)

  validation {
    condition     = length(var.github_oidc_thumbprints) > 0 && alltrue([for thumbprint in var.github_oidc_thumbprints : !startswith(thumbprint, "REPLACE_")])
    error_message = "Provide at least one real GitHub OIDC thumbprint before applying."
  }
}
variable "tags" { type = map(string) }
