<div align="center">

# ðŸš€ VentureIQ
### Autonomous Multi-Agent Startup Intelligence & Cloud Delivery Platform
**End-to-End Delivery Flow: From Multi-Agent Architecture to Containerized AWS ECS Fargate via GitHub Actions CI/CD**

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/downloads/)
[![CrewAI](https://img.shields.io/badge/CrewAI-Multi--Agent-orange.svg)](https://crewai.com)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-red.svg)](https://streamlit.io/)
[![Terraform](https://img.shields.io/badge/IaC-Terraform_v1.5+-623CE4.svg?logo=terraform&logoColor=white)](https://terraform.io)
[![AWS ECS Fargate](https://img.shields.io/badge/Compute-AWS_ECS_Fargate-FF9900.svg?logo=amazon-aws&logoColor=white)](https://aws.amazon.com/ecs/)
[![AWS ALB](https://img.shields.io/badge/Networking-Application_Load_Balancer-FF9900.svg?logo=amazon-aws&logoColor=white)](https://aws.amazon.com/elasticloadbalancing/)
[![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub_Actions_OIDC-2088FF.svg?logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

<br/>

<p align="center">
  <img src="assets/live_app.png" alt="VentureIQ Platform â€” Live on AWS ALB" width="850" />
</p>

<p align="center">
  <b>An enterprise-grade platform automating venture due diligence and startup intelligence, packaged with Docker, provisioned using Terraform, and continuously delivered to AWS with keyless GitHub Actions OIDC.</b>
</p>

</div>

---

## ðŸ“‘ Table of Contents
1. [Overview & Core Value](#-overview--core-value)
2. [End-to-End Architecture Flow](#-end-to-end-architecture-flow)
3. [Multi-Agent Swarm (AI Engine)](#-multi-agent-swarm-ai-engine)
4. [Cloud Infrastructure (Terraform & AWS)](#-cloud-infrastructure-terraform--aws)
5. [Keyless CI/CD Pipeline (GitHub Actions + OIDC)](#-keyless-cicd-pipeline-github-actions--oidc)
6. [Repository Structure](#-repository-structure)
7. [Deployment & Operations Guide](#-deployment--operations-guide)
8. [ðŸŽ¯ DevOps & Cloud Interview Guide (Q&A)](#-devops--cloud-interview-guide-qa)

---

## ðŸ“Œ Overview & Core Value

**VentureIQ** is an autonomous multi-agent intelligence platform that automates venture due diligence, market validation, and competitive research for founders, venture capital analysts, and strategy teams.

Instead of spending **30â€“50 hours** manually researching market sizing, scraping competitor landing pages, reviewing user forums, and building financial assumptions, **VentureIQ coordinates a swarm of 5 specialized AI agents** that iteratively research, cross-examine, persist findings in a vector database, and synthesize an investor-grade **8-section Master Business Analysis Report**.

The platform is containerized and delivered as a **production-grade AWS microservice** with complete infrastructure-as-code automation and zero-downtime deployment pipelines.

---

## ðŸ—ï¸ End-to-End Architecture Flow

### 1. Cloud Infrastructure & User Traffic Flow
```mermaid
flowchart TD
    subgraph Internet ["ðŸŒ Public Internet"]
        User["User Browser / Founder"]
        GH["GitHub Actions Runners"]
    end

    subgraph AWS ["â˜ï¸ Amazon Web Services (ap-south-1)"]
        subgraph PublicSubnets ["Public Subnets (AZ-a & AZ-b)"]
            ALB["Application Load Balancer (Port 80)\nIdle Timeout: 600s | Session Stickiness"]
            NAT["NAT Gateway (Outbound Internet for Tasks)"]
            IGW["Internet Gateway"]
        end

        subgraph PrivateSubnets ["Isolated Private Subnets (No Public IP)"]
            ECS["ECS Fargate Task (ventureiq-service)\n1 vCPU | 3 GB RAM\nPort: 8501 (Streamlit + CrewAI)"]
        end

        subgraph AWS_Services ["Managed AWS Services"]
            ECR["Amazon ECR (ventureiq-app)\nVulnerability Scan on Push | Lifecycle Policy"]
            SSM["AWS SSM Parameter Store\nEncrypted API Keys (GROQ, SERPER, COHERE)"]
            CW["CloudWatch Log Groups (/ecs/ventureiq)\n14-Day Log Retention"]
            S3["S3 Remote State Bucket\nVersioning & AES-256 SSE"]
            IAM["IAM Roles (Execution & Task)\nOIDC Trusted with GitHub Actions"]
        end
    end

    User -->|HTTP Port 80| ALB
    ALB -->|Streamlit Port 8501| ECS
    ECS -->|Outbound LLM / Serper Search API Calls| NAT
    NAT --> IGW
    IGW -->|External APIs| Internet

    ECS -.->|Decrypt Secrets at Runtime| SSM
    ECS -.->|Stream Logs| CW
    ECS -.->|Pull Image: latest| ECR

    GH -->|1. OIDC Token Exchange| IAM
    GH -->|2. Push Docker Image| ECR
    GH -->|3. Force ECS Rolling Deployment| ECS
```

---

## ðŸ¤– Multi-Agent Swarm (AI Engine)

VentureIQ implements a **Store-and-Summary multi-agent design pattern** to prevent context window explosion across sequential workflows:

```mermaid
sequenceDiagram
    autonumber
    actor User as User Input (Startup Idea)
    participant M as 1. Market Research Analyst
    participant C as 2. Competitor Researcher
    participant U as 3. Customer Researcher
    participant P as 4. Product Researcher
    participant B as 5. Business Analyst (Synthesizer)
    participant V as Vector Store (ChromaDB + Cohere Rerank)

    User->>M: Startup Idea Prompt
    M->>M: Web Research via Serper Google Search
    M->>V: Store Full Market Report
    M-->>C: Pass 5-Bullet Summary (Zero Context Explosion)
    
    C->>V: Query Stored Market Context (RAG)
    C->>C: Direct & Indirect Competitor Scrape
    C->>V: Store Full Competitor Report
    C-->>U: Pass 5-Bullet Summary

    U->>V: Query Market & Competitor Context
    U->>U: Build Personas, Pain Points & WTP
    U->>V: Store Customer Personas
    U-->>P: Pass 5-Bullet Summary

    P->>V: Query Customer & Competitor Context
    P->>P: Define MVP Features & Tech Stack
    P->>V: Store Product Roadmap
    P-->>B: Pass 5-Bullet Summary

    B->>V: Reranked Semantic Retrieval (Cohere v3.0)
    B->>B: Synthesize SWOT, Unit Economics & Viability Score
    B-->>User: Master 8-Section Investor Due Diligence Report
```

### The 5 Autonomous Agents:
| Agent | Role & Goal | Tools | Output Deliverables |
| :--- | :--- | :--- | :--- |
| **1. Market Analyst** | Landscape sizing & market dynamics | Serper Google Search, ChromaDB Store | TAM, SAM, SOM estimates, 5-year CAGR, growth tailwinds. |
| **2. Competitor Researcher** | Competitive intelligence & gaps | Serper Search, ScrapeWebsiteTool, RAG | Direct/indirect competitor matrix, feature flaws, pricing gaps. |
| **3. Customer Researcher** | Personas & buyer psychology | Serper Search, ScrapeWebsiteTool, RAG | ICP personas, top 5 verified pain points, willingness-to-pay tiers. |
| **4. Product Researcher** | Technical specification & MVP | Serper Search, ScrapeWebsiteTool, RAG | MoSCoW MVP feature scope, architecture stack, 3-phase roadmap. |
| **5. Business Analyst** | Due diligence & investment thesis | Cohere Reranked Semantic RAG | Master 8-section investor brief, SWOT, unit economics, viability score (1â€“10). |

---

## â˜ï¸ Cloud Infrastructure (Terraform & AWS)

The infrastructure is written entirely in **Terraform (HCL)** and split into two isolated modules:

### 1. `infra/bootstrap/` â€” Remote State & Identity Foundation
* **S3 Remote State Backend**: Provisions encrypted state bucket `ventureiq-tf-state-060002399291` with versioning and AES-256 server-side encryption.
* **GitHub Actions OIDC Provider**: Configures AWS OpenID Connect trust (`token.actions.githubusercontent.com`) for keyless authentication.
* **IAM Role (`ventureiq-github-actions-role`)**: Dynamically assumed by GitHub workflows based on repository subject claims (`repo:Sanket22g*/VentureIQ*:*`).

### 2. `infra/app/` â€” Production Application Architecture
* **Virtual Private Cloud (VPC)**:
  - CIDR: `10.0.0.0/16` deployed across 2 Availability Zones (`ap-south-1a`, `ap-south-1b`).
  - 2 Public subnets (`10.0.1.0/24`, `10.0.2.0/24`) for Load Balancers and NAT.
  - 2 Private subnets (`10.0.3.0/24`, `10.0.4.0/24`) for isolated container tasks.
  - Single NAT Gateway balancing cost efficiency with outbound API access.
* **Application Load Balancer (ALB)**:
  - Public HTTP (Port 80) listener routing to an IP-targeted ECS Target Group.
  - **600s Extended Idle Timeout**: Streamlit WebSockets remain open during long-running multi-agent reasoning chains without dropping.
  - **Session Stickiness (`lb_cookie`)**: Guarantees users stay connected to the same container instance during interactive sessions.
  - Native health checks against `/_stcore/health`.
* **Security Groups**:
  - `ventureiq-alb-sg`: Accepts public inbound traffic on HTTP port 80.
  - `ventureiq-ecs-sg`: Strictly restricts inbound port 8501 to traffic originating exclusively from the ALB security group. Outbound allowed for LLM APIs.
* **Amazon ECR Repository**:
  - `ventureiq-app` with automated image scanning on push.
  - Lifecycle policy retaining the 5 latest images to prevent storage bloat.
* **ECS Fargate Compute**:
  - Task Definition: 1 vCPU (1024 CPU units), 3 GB RAM (3072 MB) to support in-memory ChromaDB operations and CrewAI reasoning chains.
  - Desired count: 1 (scalable up to 5 instances).
* **AWS SSM Parameter Store (Secrets)**:
  - Encrypted `SecureString` parameters for `GROQ_API_KEY`, `SERPER_API_KEY`, and `COHERE_API_KEY`. Injected into task definitions at launch.
* **CloudWatch Logs**:
  - Log group `/ecs/ventureiq` with 14-day automated retention.

---

## ðŸ”„ Keyless CI/CD Pipeline (GitHub Actions + OIDC)

Instead of storing permanent AWS access keys in GitHub Secrets, VentureIQ implements **short-lived, keyless OIDC authentication**:

```mermaid
sequenceDiagram
    autonumber
    actor Dev as Developer (git push origin main)
    participant GH as GitHub Actions Runner
    participant OIDC as GitHub OIDC Token Service
    participant STS as AWS Security Token Service (STS)
    participant ECR as Amazon ECR
    participant ECS as AWS ECS Fargate

    Dev->>GH: Push commits to main branch
    GH->>OIDC: Request cryptographically signed JWT token
    OIDC-->>GH: Issue JWT with repo claims (repo:Sanket22g/VentureIQ...)
    GH->>STS: AssumeRoleWithWebIdentity (passes JWT & Role ARN)
    STS->>STS: Validate token signature & evaluate trust policy conditions
    STS-->>GH: Issue 1-hour temporary AWS credentials
    GH->>ECR: Docker build (with Astral uv) & push ventureiq-app:latest
    GH->>ECS: Trigger aws ecs update-service --force-new-deployment
    ECS->>ECR: Pull latest image
    ECS->>ECS: Zero-downtime rolling update & healthcheck verification
```

### GitHub Actions Workflows:
1. **`deploy.yaml`**: Triggers on code changes (`src/**`, `frontend/**`, `Dockerfile`). Builds container with Astral `uv`, tags, pushes to ECR, and executes an ECS rolling deployment.
2. **`infra.yaml`**: Triggers on changes to `infra/app/**`. Runs `terraform fmt`, `terraform validate`, `terraform plan`, and `terraform apply`.
3. **`destroy.yaml`**: Manual workflow with confirmation parameter to cleanly tear down AWS resources and prevent unnecessary cloud costs.

---

## ðŸ“‚ Repository Structure

```
VentureIQ/
â”œâ”€â”€ .github/
â”‚   â””â”€â”€ workflows/
â”‚       â”œâ”€â”€ deploy.yaml              # Builds Docker image, pushes to ECR, updates ECS
â”‚       â”œâ”€â”€ infra.yaml               # Terraform fmt, validate, plan, apply on infra/app
â”‚       â””â”€â”€ destroy.yaml             # Teardown workflow to stop AWS billing
â”œâ”€â”€ frontend/
â”‚   â”œâ”€â”€ .streamlit/config.toml       # Streamlit UI & theme configurations
â”‚   â”œâ”€â”€ app.py                       # Interactive analytics dashboard & telemetry
â”‚   â””â”€â”€ requirements.txt             # Lightweight frontend dependencies
â”œâ”€â”€ infra/
â”‚   â”œâ”€â”€ bootstrap/                   # S3 state bucket & GitHub Actions OIDC role
â”‚   â”‚   â”œâ”€â”€ main.tf
â”‚   â”‚   â”œâ”€â”€ variables.tf
â”‚   â”‚   â””â”€â”€ outputs.tf
â”‚   â””â”€â”€ app/                         # VPC, ALB, ECR, ECS Fargate, SSM, CloudWatch
â”‚       â”œâ”€â”€ main.tf
â”‚       â”œâ”€â”€ variables.tf
â”‚       â””â”€â”€ outputs.tf
â”œâ”€â”€ src/
â”‚   â””â”€â”€ crew_5_rag/
â”‚       â”œâ”€â”€ config/
â”‚       â”‚   â”œâ”€â”€ agents.yaml          # Agent roles, goals, and backstories
â”‚       â”‚   â””â”€â”€ tasks.yaml           # Sequential task definitions & expected outputs
â”‚       â”œâ”€â”€ tools/
â”‚       â”‚   â””â”€â”€ custom_tool.py       # ChromaDB store & Cohere reranking RAG tools
â”‚       â”œâ”€â”€ crew.py                  # CrewBase orchestration & tool bindings
â”‚       â””â”€â”€ main.py                  # CLI pipeline entry point
â”œâ”€â”€ Dockerfile                       # Multi-stage Astral uv + Python 3.11-slim image
â”œâ”€â”€ .dockerignore                    # Excludes .git, .env, .venv, local caches
â”œâ”€â”€ pyproject.toml                   # Project dependencies and packaging
â”œâ”€â”€ uv.lock                          # Deterministic dependency lockfile
â””â”€â”€ README.md                        # Documentation
```

---

## ðŸš€ Deployment & Operations Guide

### 1. Prerequisites
* AWS Account with an IAM administrative user configured locally (`aws configure`).
* Terraform `>= 1.5.0` installed.
* GitHub Repository configured.

### 2. Step 1: Bootstrap Remote State & OIDC (One-Time Setup)
```powershell
cd infra/bootstrap
terraform init
terraform apply -auto-approve
```
*Outputs: `state_bucket_name` and `github_actions_role_arn`.*

### 3. Step 2: Configure GitHub Secrets
In your GitHub repo under **Settings âž” Secrets and variables âž” Actions âž” Secrets**, add:
* `AWS_ROLE_ARN`: Output from bootstrap (e.g. `arn:aws:iam::060002399291:role/ventureiq-github-actions-role`)
* `GROQ_API_KEY`: Primary LLM API key
* `SERPER_API_KEY`: Google Search API key
* `COHERE_API_KEY`: Cohere Semantic Reranking API key

### 4. Step 3: Provision Infrastructure (`infra/app`)
```powershell
cd ../app
terraform init
terraform apply -auto-approve
```
*Outputs: `alb_dns_name`, `ecr_repository_url`, `ecs_cluster_name`, `ecs_service_name`.*

### 5. Step 4: Deploy & Verify
Push any commit to `main` branch:
```bash
git add .
git commit -m "feat: ship update"
git push origin main
```
The application will be live at your ALB DNS:
`http://ventureiq-alb-1760842476.ap-south-1.elb.amazonaws.com`

### 6. Step 5: Teardown / Cost Management
To avoid ongoing AWS charges for the NAT Gateway and ALB when testing is complete:
```powershell
cd infra/app
terraform destroy -auto-approve
```

---

##  CloudWatch Logs Live Container Observability

All Streamlit and CrewAI agent execution logs are streamed directly to **AWS CloudWatch Log Group `/ecs/ventureiq`** with 14-day automated retention. This gives full real-time visibility into agent reasoning chains, errors, and LLM API calls without needing to exec into the container.

<p align="center">
  <img src="assets/cloudwatch.png" alt="AWS CloudWatch Logs for ECS VentureIQ" width="850" />
</p>


---

## Real Agent Output - Sample Report

> **This is actual output generated by VentureIQ's 5-agent pipeline** for the startup idea: *"AI Prompt & Response Repository"*

<details>
<summary><b>Click to expand: Master Business Analysis Report</b></summary>

<br/>

## 1. Executive Summary

The proliferation of generative AI has ushered in a hyper-growth market for AI tools, prompt engineering, and AI-powered content generation. The total addressable market (TAM) for Prompt Engineering is projected at **$2-5 billion by 2030-2035**, with a serviceable obtainable market (SOM) of $2-50 million in the initial 1-3 years, growing at a **CAGR of 27-37%**.

This startup addresses critical pain points with unique differentiators: **"Prompt-to-Outcome" centricity**, comprehensive IP management frameworks, an integrated AI model sandbox for benchmarking, and advanced semantic search within AI responses.

The proposed business model is a **freemium offering transitioning to a tiered SaaS subscription**, with realistic revenue projections of **$30-50 million in Year 3**. Viability score: **8.5/10 — Build It**.

---

## 2. SWOT Analysis

| Category | Strengths | Weaknesses |
|:---|:---|:---|
| **Internal** | Addresses significant market gaps; strong product vision with "Prompt-to-Outcome" centricity; clear phased roadmap | High development complexity; high LLM API costs; reliance on third-party APIs |
| **External** | Hyper-growth market (CAGR 27-37%); first-mover advantage in prompt-to-outcome evaluation and IP solutions | Major AI providers may build similar features; regulatory hurdles on IP and data privacy |

---

## 3. Revenue Potential

| Metric | Year 1 | Year 2 | Year 3 |
|:---|:---|:---|:---|
| **Total Revenue** | **$2.5-$5M** | **$10-$20M** | **$30-$50M** |
| Active Users | 20K-50K | 100K-200K | 300K-500K |
| Conversion to Paid | 3%-5% | 5%-8% | 8%-12% |
| Blended ARPU/month | $10-$20 | $15-$30 | $20-$40 |

---

## 4. Business Model

**Freemium + Tiered SaaS Subscription:**

| Tier | Target | Key Features |
|:---|:---|:---|
| **Free** | Early adopters | Basic storage, keyword search, community upvoting |
| **Pro** | Prompt engineers, content creators | Semantic search, version control, performance metrics |
| **Enterprise** | Teams & organizations | A/B testing, IP management, API access, analytics |

---

## 5. Key Risks & Mitigations

| Risk | Mitigation |
|:---|:---|
| Regulatory & IP Ambiguity | Legal frameworks, GDPR/CCPA compliance, blockchain for content ownership |
| Intense Competition | Focus on unique differentiators: performance evaluation, IP management, AI benchmarking |
| AI Model Dependencies | Modular API-agnostic architecture; open-source LLM alternatives |
| Content Quality | Community moderation, gamification, expert contributor badges |

---

## 6. Final Verdict

> **Viability Score: 8.5 / 10 — Recommendation: Build It**

- Hyper-growth market driven by explosive generative AI adoption
- Clear problem-solution fit: fragmentation, lack of performance metrics, IP uncertainty
- Strong differentiation: "Prompt-to-Outcome" centricity, AI benchmarking sandbox
- Validated customer willingness to pay for tiered subscriptions
- Scalable model: freemium to SaaS to marketplace to enterprise

**Estimated Seed Round: $3-5 Million** to fund MVP development (6-9 months) and first 12-18 months of post-launch operations.

</details>

---

<div align="center">
  <b>Built with love by Sanket Ghadge</b>
</div>
