resource "aws_security_group" "alb" {
  name        = "${var.name}-alb"
  description = "ALB ingress"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = [var.allowed_cidr]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.allowed_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "api" {
  name   = "${var.name}-api"
  vpc_id = var.vpc_id

  ingress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }
}

resource "aws_security_group" "db" {
  name   = "${var.name}-db"
  vpc_id = var.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.api.id]
  }
}

resource "aws_security_group" "vector" {
  name   = "${var.name}-vector"
  vpc_id = var.vpc_id

  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.api.id]
  }
}

resource "aws_security_group" "qdrant" {
  name   = "${var.name}-qdrant"
  vpc_id = var.vpc_id

  ingress {
    from_port       = 6333
    to_port         = 6334
    protocol        = "tcp"
    security_groups = [aws_security_group.api.id]
  }
}

resource "aws_secretsmanager_secret" "database_app" {
  name = "${var.name}/database/app"
  tags = var.tags
}

resource "aws_secretsmanager_secret" "database_direct" {
  name = "${var.name}/database/direct"
  tags = var.tags
}

resource "aws_secretsmanager_secret" "clerk_jwt" {
  name = "${var.name}/clerk/jwt"
  tags = var.tags
}

resource "aws_secretsmanager_secret" "bedrock_api_key" {
  name = "${var.name}/bedrock/api-key"
  tags = var.tags
}

resource "aws_secretsmanager_secret" "razorpay_api" {
  name = "${var.name}/razorpay/api"
  tags = var.tags
}

resource "aws_secretsmanager_secret" "resend_api_key" {
  name = "${var.name}/resend/api-key"
  tags = var.tags
}

resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = var.github_oidc_thumbprints
}

