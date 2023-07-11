# ui.tf
resource "aws_s3_bucket" "ui_bucket" {
  bucket = "my-flutter-ui"
  acl    = "public-read"

  website {
    index_document = "index.html"
    error_document = "error.html"
  }
}

resource "aws_s3_bucket_object" "object" {
  bucket = "my-flutter-ui"
  key    = "index.html"
  source = "UI/build/web/index.html"
  acl    = "public-read"
}
