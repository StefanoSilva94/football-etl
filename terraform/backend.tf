terraform {
  backend "s3" {
    bucket = "terraform-backend-football-etl"
    key = "football-etl/terraform.tfstate"
    region = "eu-west-2"
    dynamodb_table = "terraform-locks"
    profile = "football-etl"
    # encrypt = true
  }
}