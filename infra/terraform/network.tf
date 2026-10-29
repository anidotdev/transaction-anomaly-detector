data "aws_vpc" "default" {
  default = true
}

resource "aws_security_group" "api" {
  name        = "transaction-anomaly-api-sg"
  description = "Security group for transaction API"
  vpc_id      = data.aws_vpc.default.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "FastAPI access from my IP"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["160.202.37.158/32"]
  }

  tags = {
    Project = "transaction-anomaly-detector"
  }
}

resource "aws_security_group" "worker" {
  name        = "transaction-anomaly-worker-sg"
  description = "Security group for transaction worker"
  vpc_id      = data.aws_vpc.default.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Project = "transaction-anomaly-detector"
  }
}

resource "aws_security_group" "database" {
  name        = "transaction-anomaly-db-sg"
  description = "Allow PostgreSQL only from API and worker"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description     = "PostgreSQL from API"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.api.id]
  }

  ingress {
    description     = "PostgreSQL from worker"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.worker.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Project = "transaction-anomaly-detector"
  }
}
