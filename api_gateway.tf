resource "aws_api_gateway_rest_api" "audio_notes_api" {
  name        = "audio-notes-api"
  description = "API for audio notes"

  # Enable binary media types for image uploads
  binary_media_types = [
    "image/*",
    "application/octet-stream"
  ]
}

resource "aws_api_gateway_resource" "api_resource" {
  rest_api_id = aws_api_gateway_rest_api.audio_notes_api.id
  parent_id   = aws_api_gateway_rest_api.audio_notes_api.root_resource_id
  path_part   = "upload"
}

resource "aws_api_gateway_method" "post_method" {
  rest_api_id   = aws_api_gateway_rest_api.audio_notes_api.id
  resource_id   = aws_api_gateway_resource.api_resource.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_method" "get_method" {
  rest_api_id   = aws_api_gateway_rest_api.audio_notes_api.id
  resource_id   = aws_api_gateway_resource.api_resource.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_method" "options_method" {
  rest_api_id   = aws_api_gateway_rest_api.audio_notes_api.id
  resource_id   = aws_api_gateway_resource.api_resource.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda" {
  rest_api_id = aws_api_gateway_rest_api.audio_notes_api.id
  resource_id = aws_api_gateway_resource.api_resource.id
  http_method = aws_api_gateway_method.post_method.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.save_images.invoke_arn
}

resource "aws_api_gateway_integration" "lambda_get" {
  rest_api_id = aws_api_gateway_rest_api.audio_notes_api.id
  resource_id = aws_api_gateway_resource.api_resource.id
  http_method = aws_api_gateway_method.get_method.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.get_audio.invoke_arn
}

resource "aws_api_gateway_integration" "options_integration" {
  rest_api_id = aws_api_gateway_rest_api.audio_notes_api.id
  resource_id = aws_api_gateway_resource.api_resource.id
  http_method = aws_api_gateway_method.options_method.http_method

  type = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "options_response" {
  rest_api_id = aws_api_gateway_rest_api.audio_notes_api.id
  resource_id = aws_api_gateway_resource.api_resource.id
  http_method = aws_api_gateway_method.options_method.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.audio_notes_api.id
  resource_id = aws_api_gateway_resource.api_resource.id
  http_method = aws_api_gateway_method.options_method.http_method
  status_code = aws_api_gateway_method_response.options_response.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# Method responses for POST
resource "aws_api_gateway_method_response" "post_response" {
  rest_api_id = aws_api_gateway_rest_api.audio_notes_api.id
  resource_id = aws_api_gateway_resource.api_resource.id
  http_method = aws_api_gateway_method.post_method.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
  }
}

# Method responses for GET
resource "aws_api_gateway_method_response" "get_response" {
  rest_api_id = aws_api_gateway_rest_api.audio_notes_api.id
  resource_id = aws_api_gateway_resource.api_resource.id
  http_method = aws_api_gateway_method.get_method.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
  }
}

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.save_images.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.audio_notes_api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "apigw_get" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.get_audio.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.audio_notes_api.execution_arn}/*/*"
}


resource "aws_api_gateway_deployment" "deployment" {
  depends_on = [
    aws_api_gateway_integration.lambda,
    aws_api_gateway_integration.lambda_get,
    aws_api_gateway_integration.options_integration
  ]

  rest_api_id = aws_api_gateway_rest_api.audio_notes_api.id

  # Force new deployment when configuration changes
  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.api_resource.id,
      aws_api_gateway_method.post_method.id,
      aws_api_gateway_method.get_method.id,
      aws_api_gateway_integration.lambda.id,
      aws_api_gateway_integration.lambda_get.id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "dev" {
  stage_name    = "dev"
  rest_api_id   = aws_api_gateway_rest_api.audio_notes_api.id
  deployment_id = aws_api_gateway_deployment.deployment.id
}