# ui.tf
resource "aws_s3_bucket" "ui_bucket" {
  bucket = "audio-summarizer-bucket"

  tags = {
    Name        = "audio-summarizer-bucket"
    Environment = "Dev"
  }
}

resource "aws_s3_bucket_website_configuration" "ui_bucket_website_config" {
  bucket = aws_s3_bucket.ui_bucket.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "error.html"
  }

  routing_rule {
    condition {
      key_prefix_equals = "docs/"
    }
    redirect {
      replace_key_prefix_with = "documents/"
    }
  }
}

