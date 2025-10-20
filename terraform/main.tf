terraform {
  required_version = ">= 1.5.0"
  required_providers {
    huaweicloud = {
      source  = "huaweicloud/huaweicloud"
      version = ">= 1.52.0"
    }
  }

  backend "s3" {
    bucket                      = "tf-state-autofunctiongraph"
    key                         = "fgs/functions.tfstate"
    region                      = "sa-brazil-1"
    endpoints                   = { s3 = "https://obs.sa-brazil-1.myhuaweicloud.com" }
    skip_credentials_validation = true
    skip_region_validation      = true
    skip_metadata_api_check     = true
    skip_requesting_account_id  = true
    force_path_style            = true
  }
}

provider "huaweicloud" {
  region     = var.region
  access_key = var.access_key
  secret_key = var.secret_key
  project_id = var.project_id
}

locals {
  functions = var.functions
}

resource "huaweicloud_fgs_function" "function" {
  for_each = local.functions

  name        = each.value.name
  description = lookup(each.value, "description", "")
  app         = lookup(each.value, "app", "default")
  handler     = lookup(each.value, "handler", "-")
  memory_size = lookup(each.value, "memory_size", 128)
  timeout     = lookup(each.value, "timeout", 30)

  runtime   = "Custom Image"
  agency    = each.value.agency

  custom_image {
    url = each.value.image_url
  }
}
