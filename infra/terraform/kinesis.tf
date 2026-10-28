resource "aws_kinesis_stream" "transactions" {
  name             = "paysim-transactions"
  retention_period = 24

  stream_mode_details {
    stream_mode = "ON_DEMAND"
  }

  tags = {
    Project     = "transaction-anomaly-detector"
    Environment = "development"
  }
}

output "kinesis_stream_name" {
  value = aws_kinesis_stream.transactions.name
}

output "kinesis_stream_arn" {
  value = aws_kinesis_stream.transactions.arn
}
