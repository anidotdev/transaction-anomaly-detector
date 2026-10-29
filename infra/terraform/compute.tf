data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }

  filter {
    name   = "architecture"
    values = ["x86_64"]
  }
}

resource "aws_instance" "api" {
  ami                         = data.aws_ami.amazon_linux.id
  instance_type               = "t3.micro"
  iam_instance_profile        = aws_iam_instance_profile.api.name
  vpc_security_group_ids      = [aws_security_group.api.id]
  associate_public_ip_address = true

  user_data = <<-EOF
    #!/bin/bash
    dnf update -y
    dnf install -y python3.12 python3.12-pip git
  EOF

  tags = {
    Name        = "transaction-anomaly-api"
    Project     = "transaction-anomaly-detector"
    Environment = "development"
  }
}


resource "aws_instance" "worker" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = "t3.small"
  iam_instance_profile   = aws_iam_instance_profile.worker.name
  vpc_security_group_ids = [aws_security_group.worker.id]

  user_data = <<-EOF
    #!/bin/bash
    dnf update -y
    dnf install -y python3.12 python3.12-pip git
  EOF

  tags = {
    Name        = "transaction-anomaly-worker"
    Project     = "transaction-anomaly-detector"
    Environment = "development"
  }
}
