
data "aws_subnets" "default_vpc" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

resource "aws_db_subnet_group" "paysim" {
  name       = "transaction-anomaly-db-subnets"
  subnet_ids = data.aws_subnets.default_vpc.ids

  tags = {
    Project = "transaction-anomaly-detector"
  }
}

resource "aws_db_instance" "paysim" {
  identifier     = "transaction-anomaly-paysim"
  engine         = "postgres"
  instance_class = "db.t3.micro"

  allocated_storage = 20
  storage_type      = "gp3"

  db_name  = "paysim"
  username = "paysim_admin"

  manage_master_user_password = true

  db_subnet_group_name   = aws_db_subnet_group.paysim.name
  vpc_security_group_ids = [aws_security_group.database.id]

  publicly_accessible = false
  storage_encrypted   = true

  multi_az                = false
  backup_retention_period = 0
  skip_final_snapshot     = true
  deletion_protection     = false

  tags = {
    Project     = "transaction-anomaly-detector"
    Environment = "development"
  }
}

output "database_endpoint" {
  value = aws_db_instance.paysim.address
}

output "database_port" {
  value = aws_db_instance.paysim.port
}

output "database_secret_arn" {
  value     = aws_db_instance.paysim.master_user_secret[0].secret_arn
  sensitive = true
}
