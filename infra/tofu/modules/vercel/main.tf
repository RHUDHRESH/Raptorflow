resource "terraform_data" "vercel_link" {
  input = {
    project_name   = var.project_name
    root_directory = var.root_directory
  }
}
