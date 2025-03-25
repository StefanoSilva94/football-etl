provider "aws" {
  region  = "eu-west-2"
  profile = "football-etl"
}

resource "aws_s3_bucket" "raw_football_data" {
  bucket = "football-etl-data-${random_string.suffix.result}"
  force_destroy = true
}

resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}