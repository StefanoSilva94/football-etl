provider "aws" {
  region  = "eu-west-2"
  profile = "football-etl"
}

resource "aws_s3_bucket" "raw_football_data" {
  bucket = "football-etl-data-${random_string.suffix.result}"
  force_destroy = true
}

resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

resource "aws_ecs_cluster" "football_etl_dev_fargate" {
  name = "football-etl-dev-fargate"
}

resource "aws_ecr_repository" "football_etl_repo" {
  name = "football-etl-repo"
}
#

#
resource "aws_ecs_cluster_capacity_providers" "football_etl_providers" {
  cluster_name = aws_ecs_cluster.football_etl_dev_fargate.name

  capacity_providers = ["FARGATE", "FARGATE_SPOT"]

  default_capacity_provider_strategy {
    base              = 1
    weight            = 100
    capacity_provider = "FARGATE_SPOT"
  }

  default_capacity_provider_strategy {
    base              = 0
    weight            = 0
    capacity_provider = "FARGATE"
  }
}

resource "aws_iam_role" "ecs_task_execution_role" {
  name = "ecsTaskExecutionRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy_attachment" "ecs_task_s3_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_cloudwatch_log_group" "fbref_scraper" {
  name              = "/ecs/fbref-scraper-task"
  retention_in_days = 7
}

resource "aws_ecs_task_definition" "fbref_scraper_task" {
  family                   = "fbref-scraper-task"
  cpu                      = "256"
  memory                   = "1024"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = "fb-scraper-container"
      image     = "466436411559.dkr.ecr.eu-west-2.amazonaws.com/football-etl-repo:latest"
      command   = ["/app/scrapers/fbref.py"]
      essential = true
      memory    = 1024
      memoryReservation = 1024

      environment = [
        {
          name  = "APP_ENV"
          value = "AWS"
        }
      ]

      portMappings = [
        {
          appProtocol   = "http"
          name          = "fb-scraper-container-80-tcp"
          containerPort = 80
          hostPort      = 80
          protocol      = "tcp"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.fbref_scraper.name
          awslogs-region        = "eu-west-2"
          awslogs-stream-prefix = "ecs"
          max-buffer-size       = "25m"
          mode                  = "non-blocking"
        }
      }
    }
  ])

  runtime_platform {
    cpu_architecture        = "X86_64"
    operating_system_family = "LINUX"
  }
}

resource "aws_dynamodb_table" "terraform_locks" {
  name           = "terraform-locks"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "LockID"                        # Required by Terraform - attribute to use as a partition (hash) key

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Environment = "dev"
    Purpose     = "Terraform State Locking"
  }
}