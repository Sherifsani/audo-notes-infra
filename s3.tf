resource "aws_s3_bucket" "audio_bucket" {
  bucket = var.audio-bucket-name
}

resource "aws_s3_bucket" "images_bucket" {
  bucket = var.images-bucket-name
}

resource "aws_s3_bucket_cors_configuration" "image_bucket_cors" {
  bucket = aws_s3_bucket.images_bucket.id
  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "POST", "PUT", "DELETE"]
    allowed_origins = ["*"]
    max_age_seconds = 3000
  }
}