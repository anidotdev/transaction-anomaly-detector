resource "aws_iam_policy" "api_publish_transactions" {
  name        = "transaction-anomaly-api-publish"
  description = "Allow the API to publish transaction events to Kinesis"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["kinesis:PutRecord"]
        Resource = aws_kinesis_stream.transactions.arn
      }
    ]
  })
}

resource "aws_iam_policy" "worker_consume_transactions" {
  name        = "transaction-anomaly-worker-consume"
  description = "Allow the worker to consume transaction events from Kinesis"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "kinesis:DescribeStream",
          "kinesis:GetShardIterator",
          "kinesis:GetRecords"
        ]
        Resource = aws_kinesis_stream.transactions.arn
      }
    ]
  })
}


resource "aws_iam_role" "api" {
  name = "transaction-anomaly-api-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role" "worker" {
  name = "transaction-anomaly-worker-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "api_kinesis" {
  role       = aws_iam_role.api.name
  policy_arn = aws_iam_policy.api_publish_transactions.arn
}

resource "aws_iam_role_policy_attachment" "worker_kinesis" {
  role       = aws_iam_role.worker.name
  policy_arn = aws_iam_policy.worker_consume_transactions.arn
}

resource "aws_iam_instance_profile" "api" {
  name = "transaction-anomaly-api-profile"
  role = aws_iam_role.api.name
}

resource "aws_iam_instance_profile" "worker" {
  name = "transaction-anomaly-worker-profile"
  role = aws_iam_role.worker.name
}

resource "aws_iam_role_policy_attachment" "api_ssm" {
  role       = aws_iam_role.api.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy" "api_read_database_secret" {
  name = "transaction-anomaly-api-read-db-secret"
  role = aws_iam_role.api.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = aws_db_instance.paysim.master_user_secret[0].secret_arn
      }
    ]
  })
}
