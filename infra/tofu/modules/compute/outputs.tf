output "cluster_name" { value = aws_ecs_cluster.this.name }
output "service_name" { value = aws_ecs_service.api.name }
output "load_balancer_dns_name" { value = aws_lb.api.dns_name }
output "qdrant_service_name" { value = aws_ecs_service.qdrant.name }
output "qdrant_service_discovery_namespace" { value = aws_service_discovery_private_dns_namespace.this.name }
output "alb_logs_bucket_name" { value = aws_s3_bucket.alb_logs.bucket }

