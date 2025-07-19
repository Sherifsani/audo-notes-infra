resource "aws_iam_role" "lambda_role" {
  name = "audio_notes_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

}

resource "aws_iam_role" "extract_images_role" {
  name = "extract_images_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

}

resource "aws_iam_role" "get_images_role" {
  name = "get_audio_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

}

resource "aws_iam_role_policy_attachment" "lambda_role_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "extract_images_role_policy_attachment" {
  role       = aws_iam_role.extract_images_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"

}

resource "aws_iam_role_policy_attachment" "get_images_role_policy_attachment" {
  role       = aws_iam_role.get_images_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_policy" "lambda_s3_policy" {
  name        = "lambda_s3_policy"
  description = "allows lambda function create buckets and save images to them"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:*",
        ]
        Resource = [
          "arn:aws:s3:::*"
        ]
      }
    ]
  })
}

resource "aws_iam_policy" "lambda_textract_policy" {
  name        = "lambda_textract_policy"
  description = "allows lambda function to use Textract"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "textract:*"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_get_images_policy_attachment" {
  role       = aws_iam_role.get_images_role.name
  policy_arn = aws_iam_policy.lambda_s3_policy.arn

}
resource "aws_iam_role_policy_attachment" "lambda_s3_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_s3_policy.arn
}

resource "aws_iam_role_policy_attachment" "lambda_textract_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_textract_policy.arn
}

resource "aws_iam_policy_attachment" "lambda_s3_textract_policy" {
  name       = "lambda-policy-attachment"
  roles      = [aws_iam_role.extract_images_role.name]
  policy_arn = aws_iam_policy.lambda_s3_textract.arn
}

resource "aws_iam_policy" "lambda_s3_textract" {
  name        = "LambdaS3TextractPolicy"
  description = "Allow Lambda to use S3 and Textract"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:GetObject"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = [
          "textract:DetectDocumentText"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = [
          "polly:SynthesizeSpeech"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = [
          "s3:PutObject"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "*"
      }
    ]
  })
}