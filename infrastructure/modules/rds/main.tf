# =====================================================
# RDS POSTGRES MODULE
# =====================================================

resource "aws_db_subnet_group" "main" {
  name       = "raptorflow-db-${var.environment}"
  subnet_ids = var.private_subnet_ids

  tags = {
    Name = "raptorflow-db-subnet-group-${var.environment}"
  }
}

resource "aws_security_group" "rds" {
  name_prefix = "raptorflow-rds-"
  description = "Security group for RDS PostgreSQL"
  vpc_id      = var.vpc_id

  ingress {
    description     = "Allow PostgreSQL access from ECS tasks"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = var.allowed_security_groups
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "raptorflow-rds-sg-${var.environment}"
  }
}

resource "aws_db_parameter_group" "main" {
  family = "postgres15"
  name   = "raptorflow-postgres-${var.environment}"

  parameter {
    name  = "log_statement"
    value = "all"
  }

  parameter {
    name  = "log_min_duration_statement"
    value = "1000"
  }

  parameter {
    name  = "shared_preload_libraries"
    value = "pg_stat_statements"
  }

  tags = {
    Name = "raptorflow-postgres-params-${var.environment}"
  }
}

resource "aws_db_instance" "main" {
  identifier = "raptorflow-postgres-${var.environment}"

  # Engine configuration
  engine         = "postgres"
  engine_version = "15.7"
  instance_class = var.instance_class

  # Storage
  allocated_storage     = var.allocated_storage
  max_allocated_storage = var.max_allocated_storage
  storage_type          = "gp3"
  storage_encrypted     = true
  kms_key_id           = var.kms_key_arn

  # Database configuration
  db_name  = var.database_name
  username = var.database_username
  password = var.database_password
  port     = 5432

  # Network
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = false

  # Maintenance & backup
  maintenance_window              = "sun:03:00-sun:04:00"
  backup_window                  = "02:00-03:00"
  backup_retention_period        = var.environment == "prod" ? 30 : 7
  copy_tags_to_snapshot          = true
  delete_automated_backups       = var.environment != "prod"
  deletion_protection            = var.environment == "prod"
  skip_final_snapshot            = var.environment != "prod"
  final_snapshot_identifier      = var.environment == "prod" ? "raptorflow-postgres-final-${var.environment}" : null

  # Monitoring
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  monitoring_interval            = 60
  monitoring_role_arn           = aws_iam_role.rds_enhanced_monitoring.arn
  performance_insights_enabled  = true
  performance_insights_kms_key_id = var.kms_key_arn

  # Parameter group
  parameter_group_name = aws_db_parameter_group.main.name

  tags = {
    Name = "raptorflow-postgres-${var.environment}"
  }
}

# IAM role for RDS enhanced monitoring
resource "aws_iam_role" "rds_enhanced_monitoring" {
  name = "raptorflow-rds-enhanced-monitoring-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "raptorflow-rds-monitoring-${var.environment}"
  }
}

resource "aws_iam_role_policy_attachment" "rds_enhanced_monitoring" {
  role       = aws_iam_role.rds_enhanced_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# CloudWatch alarms for RDS
resource "aws_cloudwatch_metric_alarm" "rds_cpu" {
  alarm_name          = "raptorflow-rds-cpu-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "RDS CPU utilization is too high"

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }
}

resource "aws_cloudwatch_metric_alarm" "rds_free_storage" {
  alarm_name          = "raptorflow-rds-free-storage-${var.environment}"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "2000000000" # 2GB in bytes
  alarm_description   = "RDS free storage space is low"

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }
}

