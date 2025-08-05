# API Gateway outputs
output "api_gateway_url" {
  description = "Base URL for API Gateway stage"
  value       = aws_api_gateway_stage.dev.invoke_url
}

output "api_endpoints" {
  description = "Available API endpoints"
  value = {
    notes_post = "${aws_api_gateway_stage.dev.invoke_url}/notes"
    notes_get  = "${aws_api_gateway_stage.dev.invoke_url}/notes"
  }
}

output "api_gateway_id" {
  description = "ID of the API Gateway"
  value       = aws_api_gateway_rest_api.audio_notes_api.id
}
