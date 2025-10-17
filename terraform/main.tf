terraform {
  required_version = ">= 1.5.0"
  required_providers {
    huaweicloud = {
      source  = "huaweicloud/huaweicloud"
      version = ">= 1.52.0"
    }
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
  description = each.value.description
  package     = "default"
  handler     = each.value.handler
  memory_size = each.value.memory_size
  timeout     = each.value.timeout

  runtime = each.value.runtime

  code {
    image = each.value.image
  }
}
