# Monitoring Module Outputs

output "dashboard_url" {
  description = "CloudWatch dashboard URL"
  value       = "https://${var.region}.console.aws.amazon.com/cloudwatch/home?region=${var.region}#dashboards:name=${var.environment}-raptorflow-unified"
}

output "alerts_topic_arn" {
  description = "SNS topic ARN for alerts"
  value       = var.enable_alarms ? aws_sns_topic.alerts[0].arn : null
}


