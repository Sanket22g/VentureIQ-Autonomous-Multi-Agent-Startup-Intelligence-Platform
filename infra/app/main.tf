terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket = "ventureiq-tf-state-060002399291"
    key    = "app/terraform.tfstate"
    region = "ap-south-1"
  }
}

provider "aws" {
  region = var.aws_region
}

# ── 1. VPC & Networking ────────────────────────────────────────────────────────
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "ventureiq-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["${var.aws_region}a", "${var.aws_region}b"]
  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnets = ["10.0.3.0/24", "10.0.4.0/24"]

  # One NAT Gateway shared across private subnets to balance outbound internet access with cost efficiency
  enable_nat_gateway   = true
  single_nat_gateway   = true
  enable_dns_hostnames = true

  tags = {
    Project     = "VentureIQ"
    Environment = "Production"
  }
}

# ── 2. Amazon ECR Repository ──────────────────────────────────────────────────
resource "aws_ecr_repository" "ventureiq" {
  name                 = var.ecr_repository
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Project = "VentureIQ"
  }
}

resource "aws_ecr_lifecycle_policy" "ventureiq" {
  repository = aws_ecr_repository.ventureiq.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Retain the latest 5 container images"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 5
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

# ── 3. Security Groups ─────────────────────────────────────────────────────────
# Application Load Balancer Security Group (Accepts Public HTTP Traffic)
resource "aws_security_group" "alb" {
  name        = "ventureiq-alb-sg"
  description = "Allows public inbound traffic on HTTP port 80"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description = "Allow inbound HTTP from anywhere"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "ventureiq-alb-sg"
    Project = "VentureIQ"
  }
}

# ECS Fargate Tasks Security Group (Isolated, Only Accepts Traffic from ALB)
resource "aws_security_group" "ecs" {
  name        = "ventureiq-ecs-sg"
  description = "Allows inbound traffic only from the ALB to Streamlit on port 8501"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description     = "Allow Streamlit port 8501 strictly from ALB"
    from_port       = 8501
    to_port         = 8501
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    description = "Allow all outbound traffic for external LLM & Google search APIs"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "ventureiq-ecs-sg"
    Project = "VentureIQ"
  }
}

# ── 4. Application Load Balancer (ALB) ─────────────────────────────────────────
resource "aws_lb" "ventureiq" {
  name               = "ventureiq-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = module.vpc.public_subnets

  # Extended 600s timeout prevents dropping Streamlit WebSockets during multi-agent Crew runs
  idle_timeout = 600

  tags = {
    Name    = "ventureiq-alb"
    Project = "VentureIQ"
  }
}

resource "aws_lb_target_group" "ventureiq" {
  name        = "ventureiq-tg"
  port        = 8501
  protocol    = "HTTP"
  vpc_id      = module.vpc.vpc_id
  target_type = "ip"

  # Native Streamlit health check
  health_check {
    path                = "/_stcore/health"
    protocol            = "HTTP"
    port                = "8501"
    matcher             = "200"
    interval            = 30
    timeout             = 10
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }

  # Stickiness ensures active Streamlit sessions remain connected to the same container
  stickiness {
    type            = "lb_cookie"
    cookie_duration = 86400
    enabled         = true
  }

  tags = {
    Project = "VentureIQ"
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.ventureiq.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ventureiq.arn
  }
}

# ── 5. CloudWatch Logs ────────────────────────────────────────────────────────
resource "aws_cloudwatch_log_group" "ventureiq" {
  name              = "/ecs/ventureiq"
  retention_in_days = 14

  tags = {
    Project = "VentureIQ"
  }
}

# ── 6. Secrets Management (AWS Systems Manager Parameter Store) ────────────────
resource "aws_ssm_parameter" "groq_key" {
  name        = "/ventureiq/GROQ_API_KEY"
  description = "Groq API key for primary LLM inference"
  type        = "SecureString"
  value       = var.groq_api_key

  tags = {
    Project = "VentureIQ"
  }
}

resource "aws_ssm_parameter" "serper_key" {
  name        = "/ventureiq/SERPER_API_KEY"
  description = "SerperDev API key for Google Search tool"
  type        = "SecureString"
  value       = var.serper_api_key

  tags = {
    Project = "VentureIQ"
  }
}

resource "aws_ssm_parameter" "cohere_key" {
  name        = "/ventureiq/COHERE_API_KEY"
  description = "Cohere API key for RAG reranking"
  type        = "SecureString"
  value       = var.cohere_api_key

  tags = {
    Project = "VentureIQ"
  }
}

# ── 7. IAM Roles for ECS ──────────────────────────────────────────────────────
# Task Execution Role (used by ECS agent to pull images, stream logs, read secrets)
resource "aws_iam_role" "ecs_execution" {
  name = "ventureiq-ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_base" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Grant execution role access to read encrypted SSM parameters
resource "aws_iam_role_policy" "ecs_ssm_read" {
  name = "ventureiq-ssm-parameters-read"
  role = aws_iam_role.ecs_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameters",
          "ssm:GetParameter"
        ]
        Resource = "arn:aws:ssm:${var.aws_region}:*:parameter/ventureiq/*"
      }
    ]
  })
}

# Task Role (used by the running container if application needs direct AWS SDK access)
resource "aws_iam_role" "ecs_task" {
  name = "ventureiq-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# ── 8. ECS Cluster ────────────────────────────────────────────────────────────
resource "aws_ecs_cluster" "ventureiq" {
  name = var.ecs_cluster

  tags = {
    Project = "VentureIQ"
  }
}

# ── 9. ECS Task Definition ────────────────────────────────────────────────────
resource "aws_ecs_task_definition" "ventureiq" {
  family                   = var.ecs_task_family
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "1024" # 1 vCPU
  memory                   = "3072" # 3 GB RAM (suitable for ChromaDB and CrewAI agents)

  execution_role_arn = aws_iam_role.ecs_execution.arn
  task_role_arn      = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = var.ecs_container_name
      image     = "${aws_ecr_repository.ventureiq.repository_url}:latest"
      essential = true

      portMappings = [
        {
          containerPort = 8501
          hostPort      = 8501
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "MODEL"
          value = var.model_name
        },
        {
          name  = "CREWAI_TRACING_ENABLED"
          value = "false"
        }
      ]

      secrets = [
        {
          name      = "GROQ_API_KEY"
          valueFrom = aws_ssm_parameter.groq_key.arn
        },
        {
          name      = "SERPER_API_KEY"
          valueFrom = aws_ssm_parameter.serper_key.arn
        },
        {
          name      = "COHERE_API_KEY"
          valueFrom = aws_ssm_parameter.cohere_key.arn
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ventureiq.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])

  tags = {
    Project = "VentureIQ"
  }
}

# ── 10. ECS Service ───────────────────────────────────────────────────────────
resource "aws_ecs_service" "ventureiq" {
  name            = var.ecs_service
  cluster         = aws_ecs_cluster.ventureiq.id
  task_definition = aws_ecs_task_definition.ventureiq.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = module.vpc.private_subnets
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.ventureiq.arn
    container_name   = var.ecs_container_name
    container_port   = 8501
  }

  depends_on = [aws_lb_listener.http]

  tags = {
    Project = "VentureIQ"
  }
}
