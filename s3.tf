resource "aws_s3_bucket" "audio_bucket" {
  bucket = var.audio-bucket-name
}

resource "aws_s3_bucket" "images_bucket" {
  bucket = var.images-bucket-name
}