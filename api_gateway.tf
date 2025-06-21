resource "aws_api_gateway_rest_api" "audio_notes_api" {
  name = "audio-notes-api"
  description = "API for audio notes"
}

resource "aws_api_gateway_resource" "api_resource" {
  rest_api_id = aws_api_gateway_rest_api.audio_notes_api.id
  parent_id = aws_api_gateway_rest_api.audio_notes_api.root_resource_id
  path_part = "upload-notes"
}

resource "aws_api_gateway_method" "post_method" {
  rest_api_id = aws_api_gateway_rest_api.audio_notes_api.id
  resource_id = aws_api_gateway_resource.api_resource.id
  http_method = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_method" "get_method" {
  rest_api_id = aws_api_gateway_rest_api.audio_notes_api.id
  resource_id = aws_api_gateway_resource.api_resource.id
  http_method = "GET"
  authorization = "NONE"
}