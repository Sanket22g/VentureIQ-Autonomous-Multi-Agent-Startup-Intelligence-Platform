variable "aws_region" {
  description = "AWS Region to deploy resources"
  type        = string
  default     = "ap-south-1"
}

variable "state_bucket_name" {
  description = "Globally unique name for the S3 bucket storing Terraform state"
  type        = string
  default     = "ventureiq-tf-state-060002399291"
}

variable "github_org" {
  description = "GitHub user or organization name"
  type        = string
  default     = "Sanket22g"
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
  default     = "VentureIQ-Autonomous-Multi-Agent-Startup-Intelligence-Platform"
}
