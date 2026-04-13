resource "aws_db_subnet_group" "aurora" {
  name       = "${var.name}-aurora"
  subnet_ids = var.database_subnet_ids
  tags       = var.tags
}

resource "aws_rds_cluster" "aurora" {
  cluster_identifier                  = "${var.name}-aurora"
  engine                              = "aurora-postgresql"
  engine_mode                         = "provisioned"
  engine_version                      = "16.8"
  database_name                       = var.db_name
  master_username                     = var.db_username
  manage_master_user_password         = true
  db_subnet_group_name                = aws_db_subnet_group.aurora.name
  vpc_security_group_ids              = [var.db_security_group_id]
  storage_encrypted                   = true
  serverlessv2_scaling_configuration {
    min_capacity = 0.5
    max_capacity = 8
  }
}

resource "aws_rds_cluster_instance" "writer" {
  identifier         = "${var.name}-aurora-writer"
  cluster_identifier = aws_rds_cluster.aurora.id
  instance_class     = "db.serverless"
  engine             = aws_rds_cluster.aurora.engine
  engine_version     = aws_rds_cluster.aurora.engine_version
}

resource "aws_sqs_queue" "embedding" {
  name                       = "${var.name}-embedding"
  message_retention_seconds  = 345600
  visibility_timeout_seconds = 120
}

resource "aws_sqs_queue" "content_pregeneration" {
  name                       = "${var.name}-content-pregeneration"
  message_retention_seconds  = 345600
  visibility_timeout_seconds = 120
}

resource "aws_s3_bucket" "primary" {
  bucket = "${var.name}-artifacts"
  tags   = var.tags
}

resource "aws_s3_bucket_public_access_block" "primary" {
  bucket                  = aws_s3_bucket.primary.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "primary" {
  bucket = aws_s3_bucket.primary.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_versioning" "primary" {
  bucket = aws_s3_bucket.primary.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "primary" {
  bucket = aws_s3_bucket.primary.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "primary" {
  bucket = aws_s3_bucket.primary.id

  rule {
    id     = "expire-noncurrent-versions"
    status = "Enabled"

    noncurrent_version_expiration {
      noncurrent_days = 30
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

resource "aws_s3_bucket_logging" "primary" {
  bucket = aws_s3_bucket.primary.id

  target_bucket = aws_s3_bucket.primary_logs.id
  target_prefix = "primary/"
}

resource "aws_s3_bucket" "primary_logs" {
  bucket = "${var.name}-artifacts-logs"
  tags   = var.tags
}

resource "aws_s3_bucket_public_access_block" "primary_logs" {
  bucket                  = aws_s3_bucket.primary_logs.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "primary_logs" {
  bucket = aws_s3_bucket.primary_logs.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_versioning" "primary_logs" {
  bucket = aws_s3_bucket.primary_logs.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "primary_logs" {
  bucket = aws_s3_bucket.primary_logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_efs_file_system" "qdrant" {
  creation_token = "${var.name}-qdrant"
  encrypted      = true
  tags           = var.tags
}

resource "aws_efs_mount_target" "qdrant" {
  for_each        = toset(var.private_subnet_ids)
  subnet_id       = each.value
  file_system_id   = aws_efs_file_system.qdrant.id
  security_groups = [var.qdrant_security_group_id]
}

resource "aws_instance" "dragonfly" {
  ami                    = var.dragonfly_ami_id
  instance_type          = "m5.large"
  subnet_id              = var.private_subnet_ids[0]
  vpc_security_group_ids = [var.dragonfly_security_group_id]
  tags                   = merge(var.tags, { Name = "${var.name}-dragonfly" })

  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }

  root_block_device {
    encrypted             = true
    volume_size           = 30
    volume_type           = "gp3"
    delete_on_termination = true
  }
}
