# Auto FunctionGraph

Auto FunctionGraph accelerates building and deploying containerized functions to Huawei Cloud FunctionGraph. The repository is organized so that each function lives in its own project folder, with automated CI/CD that builds Docker images, publishes them to Software Repository for Container (SWR), and applies Terraform to provision or update the corresponding FunctionGraph functions.

## Repository structure

```
.
├── .github/workflows/deploy.yml   # GitHub Actions workflow for building and deploying
├── projects/                      # One subfolder per FunctionGraph function
│   └── sample-function/           # Example function implementation
│       ├── Dockerfile             # Container definition used by FunctionGraph
│       └── src/app.py             # Example Python handler (app.handler)
└── terraform/                     # Terraform IaC for FunctionGraph resources
    ├── main.tf                    # Provider and function resource definitions
    └── variables.tf               # Input variables for the deployment
```

## Getting started

1. **Install prerequisites**
   - Docker for building container images locally.
   - Terraform ≥ 1.5.
   - Huawei Cloud CLI tools (optional, for local validation).

2. **Create a new function project**
   - Duplicate `projects/sample-function` and rename it to match your function name.
   - Update the `Dockerfile` and handler source code under `src/` to fit your runtime.
   - Ensure the Docker container exposes a handler compatible with FunctionGraph.

3. **Configure Terraform variables**
   - Copy `terraform/variables.tf` to create a `terraform/terraform.tfvars` file (not committed) or provide variables through environment variables:
     ```hcl
     region      = "<your-region>"
     project_id  = "<your-project-id>"
     access_key  = "<huaweicloud-access-key>"
     secret_key  = "<huaweicloud-secret-key>"
     functions = {
       sample-function = {
         name        = "sample-function"
         description = "Sample function managed by Auto FunctionGraph"
         handler     = "app.handler"
         runtime     = "Python3.10"
         memory_size = 256
         timeout     = 30
         image       = "<swr-endpoint>/<organization>/sample-function:<tag>"
       }
     }
     ```

4. **Apply infrastructure locally (optional)**
   ```bash
   cd terraform
   terraform init
   terraform apply
   ```

## Continuous deployment pipeline

The GitHub Actions workflow in `.github/workflows/deploy.yml` performs the following steps whenever changes land on the `main` branch:

1. Checks out the repository.
2. Configures Docker Buildx and logs in to the target SWR registry.
3. Iterates through every directory inside `projects/`, builds a Docker image for each function, tags it with the current commit SHA, and pushes it to SWR under the configured organization (and optional namespace).
4. Generates `terraform/functions.auto.tfvars.json` so Terraform has the latest image URIs and default function settings.
5. Runs `terraform init` and `terraform apply` to create or update FunctionGraph functions using the uploaded images.

### Required secrets

Store the following secrets in your repository settings for the workflow to succeed:

| Secret | Description |
| ------ | ----------- |
| `HUAWEICLOUD_REGION` | Target Huawei Cloud region. |
| `HUAWEICLOUD_PROJECT_ID` | Huawei Cloud project ID where FunctionGraph functions will be created. |
| `HUAWEICLOUD_ACCESS_KEY` | Access key for Huawei Cloud credentials. |
| `HUAWEICLOUD_SECRET_KEY` | Secret key for Huawei Cloud credentials. |
| `SWR_ENDPOINT` | Fully qualified SWR registry endpoint (e.g., `swr.ap-southeast-1.myhuaweicloud.com`). |
| `SWR_ORGANIZATION` | SWR organization that owns the image repositories. |
| `SWR_NAMESPACE` | Optional additional namespace or folder beneath the organization. |
| `SWR_USERNAME` | Username for authenticating to SWR. |
| `SWR_PASSWORD` | Password or access token for SWR authentication. |

If you do not organize repositories under a secondary namespace, you can omit `SWR_NAMESPACE` and it will be ignored.

## Local development tips

- Keep each function self-contained within its project folder, including dependencies and build context.
- Use consistent handler naming so the CI pipeline can auto-populate Terraform defaults, or adjust the workflow script if you need per-function customization.
- Add additional Terraform configuration (e.g., triggers, aliases, logging) inside the `terraform/` directory as needed.
- Commit only source files—avoid committing generated files such as `terraform/functions.auto.tfvars.json` or Terraform state.

## Next steps

- Add more function projects under `projects/` as your application grows.
- Extend the GitHub Actions workflow to include automated testing or security scans before deployment.
- Integrate notifications (Slack, email) to monitor deployment outcomes.
