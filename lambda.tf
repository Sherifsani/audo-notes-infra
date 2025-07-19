data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/lambda/save_images.py"
  output_path = "${path.module}/lambda/save_images.zip"
}

resource "aws_lambda_function" "save_images" {
  function_name    = "save-Images-Function"
  role             = aws_iam_role.lambda_role.arn
  handler          = "save_images.lambda_handler"
  runtime          = "python3.8"
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  timeout          = 10

  environment {
    variables = {
      IMAGES_BUCKET = var.images-bucket-name
    }
  }
}

data "archive_file" "extract_images" {
  type        = "zip"
  source_file = "${path.module}/lambda/extract_images.py"
  output_path = "${path.module}/lambda/extract_images.zip"
}

resource "aws_lambda_function" "extract_images" {
  function_name    = "extract-Images-Function"
  role             = aws_iam_role.extract_images_role.arn
  handler          = "extract_images.lambda_handler"
  runtime          = "python3.12"
  filename         = data.archive_file.extract_images.output_path
  source_code_hash = data.archive_file.extract_images.output_base64sha256
  timeout          = 10

  environment {
    variables = {
      AUDIO_BUCKET = var.audio-bucket-name
    }
  }
}

data "archive_file" "get_images" {
  type        = "zip"
  source_file = "${path.module}/lambda/get_images.py"
  output_path = "${path.module}/lambda/get_images.zip"
}


resource "aws_lambda_function" "get_images" {
  function_name = "get-Images-Function"
  role = aws_iam_role.get_images_role.arn
  handler = "get_images.lambda_handler"
  runtime = "python3.12"
  filename = data.archive_file.get_images.output_path
  source_code_hash = data.archive_file.get_images.output_base64sha256
  timeout = 10

  environment {
    variables = {
      AUDIO_BUCKET = var.audio-bucket-name
    }
  }
}
resource "aws_lambda_permission" "allow_s3_invoke" {
  statement_id  = "AllowExecutionFromS3"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.extract_images.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = "arn:aws:s3:::images-bucket-1234"
}

resource "aws_s3_bucket_notification" "trigger_extract_function" {
  bucket = "images-bucket-1234"

  lambda_function {
    lambda_function_arn = aws_lambda_function.extract_images.arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".jpg"
  }

  depends_on = [aws_lambda_permission.allow_s3_invoke]
}