provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Project     = "atlas"
      Environment = var.environment
      ManagedBy   = "terraform"
      Owner       = "atlas-team"
    }
  }
}
