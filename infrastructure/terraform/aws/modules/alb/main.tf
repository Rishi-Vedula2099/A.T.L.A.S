locals {
  tags = merge({ Layer = "alb" }, var.tags)
}

# Internet-facing ALB serving the frontend + API.
resource "aws_lb" "this" {
  name               = "${var.name_prefix}-${var.environment}"
  internal           = false
  load_balancer_type = "application"
  subnets            = var.subnet_ids
  ip_address_type    = "ipv4"

  drop_invalid_header_fields = true

  tags = local.tags
}

# Default target group — backend. The frontend gets its own target group below.
resource "aws_lb_target_group" "backend" {
  name     = "${var.name_prefix}-backend"
  port     = var.backend_port
  protocol = "HTTP"
  vpc_id   = var.vpc_id

  health_check {
    enabled             = true
    path                = var.health_check_path
    port                = "traffic-port"
    protocol            = "HTTP"
    interval            = 15
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
    matcher             = "200"
  }

  stickiness {
    type            = "lb_cookie"
    cookie_duration = 86400
    enabled         = true # sticky for WebSocket /readyz sessions
  }

  tags = local.tags
}

resource "aws_lb_target_group" "frontend" {
  name     = "${var.name_prefix}-frontend"
  port     = var.frontend_port
  protocol = "HTTP"
  vpc_id   = var.vpc_id

  health_check {
    enabled  = true
    path     = "/api/health"
    protocol = "HTTP"
    matcher  = "200"
  }

  tags = local.tags
}

# HTTPS listener — set certificate_arn on the CLI via -var.
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.this.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  # certificate_arn = var.certificate_arn   # TODO: wire from ACM module / route53

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.frontend.arn
  }
}

resource "aws_lb_listener_rule" "api" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 100

  condition {
    host_header {
      values = ["api.*"]
    }
  }

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }
}

# HTTP -> HTTPS redirect.
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.this.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}
