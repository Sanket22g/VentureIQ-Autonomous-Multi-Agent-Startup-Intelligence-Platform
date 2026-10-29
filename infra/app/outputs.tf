output "alb_dns_name" {
  description = "The public web URL of your VentureIQ Streamlit Dashboard"
  value       = "http://${aws_lb.ventureiq.dns_name}"
}

output "ecr_repository_url" {
  description = "The Amazon ECR Docker repository URL"
  value       = aws_ecr_repository.ventureiq.repository_url
}

output "ecs_cluster_name" {
  description = "Name of the deployed ECS cluster"
  value       = aws_ecs_cluster.ventureiq.name
}

output "ecs_service_name" {
  description = "Name of the deployed ECS service"
  value       = aws_ecs_service.ventureiq.name
}
