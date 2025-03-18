terraform {
  backend "gcs" {
    bucket = "qwiklabs-gcp-04-6f5021a88bbb-terraform-state"
    prefix = "prod"
  }
}
