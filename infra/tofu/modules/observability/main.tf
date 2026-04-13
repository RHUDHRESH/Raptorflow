resource "aws_cloudwatch_dashboard" "platform" {
  dashboard_name = "${var.name}-platform"
  dashboard_body = jsonencode({
    widgets = [
      {
        type = "text"
        x    = 0
        y    = 0
        width = 24
        height = 4
        properties = {
          markdown = "RaptorFlow platform dashboard scaffold for ${var.cluster_name} (${var.load_balancer_dns_name})"
        }
      }
    ]
  })
}

resource "aws_cloudwatch_metric_alarm" "api_unhealthy" {
  alarm_name          = "${var.name}-api-unhealthy"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 1
  metric_name         = "HealthyHostCount"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Average"
  threshold           = 1
  alarm_description   = "API healthy host count dropped below 1"
}
