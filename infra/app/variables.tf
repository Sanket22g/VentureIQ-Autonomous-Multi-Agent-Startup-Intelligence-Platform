variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-south-1"
}

variable "ecr_repository" {
  description = "Name of the ECR repository"
  type        = string
  default     = "ventureiq-app"
}

variable "ecs_cluster" {
  description = "Name of the ECS cluster"
  type        = string
  default     = "ventureiq-cluster"
}

variable "ecs_service" {
  description = "Name of the ECS service"
  type        = string
  default     = "ventureiq-service"
}

variable "ecs_task_family" {
  description = "Family name of the ECS task definition"
  type        = string
  default     = "ventureiq-task"
}

variable "ecs_container_name" {
  description = "Container name inside task definition"
  type        = string
  default     = "ventureiq-container"
}

variable "model_name" {
  description = "Primary LLM model name used by CrewAI"
  type        = string
  default     = "groq/openai/gpt-oss-120b"
}

# API Keys injected securely via terraform.tfvars or GitHub Secrets
variable "groq_api_key" {
  description = "Groq API Key"
  type        = string
  sensitive   = true
}

variable "serper_api_key" {
  description = "SerperDev Google Search API Key"
  type        = string
  sensitive   = true
}

variable "cohere_api_key" {
  description = "Cohere API Key for Rerank"
  type        = string
  sensitive   = true
}
