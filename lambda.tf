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
}