output "aurora_cluster_arn" { value = aws_rds_cluster.aurora.arn }
output "embedding_queue_url" { value = aws_sqs_queue.embedding.url }
output "content_pregeneration_queue_url" { value = aws_sqs_queue.content_pregeneration.url }
output "primary_bucket_name" { value = aws_s3_bucket.primary.bucket }
output "qdrant_efs_id" { value = aws_efs_file_system.qdrant.id }

