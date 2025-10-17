variable "region" {
  description = "Huawei Cloud region to deploy resources in."
  type        = string
}

variable "project_id" {
  description = "Project ID where FunctionGraph functions should be created."
  type        = string
}

variable "access_key" {
  description = "Access key for Huawei Cloud authentication."
  type        = string
  sensitive   = true
}

variable "secret_key" {
  description = "Secret key for Huawei Cloud authentication."
  type        = string
  sensitive   = true
}

variable "functions" {
  description = "Map of FunctionGraph function definitions keyed by logical name."
  type = map(object({
    name        = string
    description = optional(string, "")
    handler     = string
    runtime     = string
    memory_size = optional(number, 128)
    timeout     = optional(number, 30)
    image       = string
  }))
}
