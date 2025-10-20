region         = "sa-brazil-1"
project_id     = "your-project-id"
access_key     = "your-access-key"
secret_key     = "your-secret-key"
security_token = ""

functions = {
  sample-function = {
    name        = "sample-function"
    description = "Sample FunctionGraph deployment"
    agency      = "functiongraph_agency"
    app         = "default"
    handler     = "-"
    memory_size = 256
    timeout     = 60
    image_url   = "swr.sa-brazil-1.myhuaweicloud.com/auto-functiongraph/sample-function:latest"
  }
}
