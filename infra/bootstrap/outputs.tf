output "github_actions_role_arn" {
  description = "The ARN of the IAM role to set as AWS_ROLE_ARN in GitHub Secrets"
  value       = aws_iam_role.github_actions.arn
}

output "state_bucket_name" {
  description = "The S3 bucket name created for Terraform remote state"
  value       = aws_s3_bucket.tf_state.bucket
}

output "aws_region" {
  description = "AWS region configured"
  value       = var.aws_region
}
