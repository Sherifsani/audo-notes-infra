# Audio Notes - Image to Speech Converter

![Architecture](https://img.shields.io/badge/AWS-Lambda-orange) ![React](https://img.shields.io/badge/React-TypeScript-blue) ![Terraform](https://img.shields.io/badge/Infrastructure-Terraform-purple)

A serverless web application that converts images containing text into audio using AWS AI services. Upload an image with text, and the system will extract the text using OCR and convert it to speech.

## 🎯 Features

- **Image Text Extraction**: Automatically extract text from uploaded images using AWS Textract
- **Text-to-Speech Conversion**: Convert extracted text to natural-sounding audio using AWS Polly
- **Serverless Architecture**: Built on AWS Lambda for automatic scaling and cost efficiency
- **Modern Web Interface**: React TypeScript frontend with responsive design
- **Real-time Processing**: S3 event-driven architecture for immediate processing
- **Infrastructure as Code**: Complete AWS infrastructure defined using Terraform

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Client  │    │   API Gateway   │    │  Lambda Functions│
│                 │───▶│                 │───▶│                 │
│ - Image Upload  │    │ - Upload URLs   │    │ - Save Images   │
│ - Audio Player  │    │ - CORS Config   │    │ - Extract Text  │
└─────────────────┘    └─────────────────┘    │ - Get Audio     │
                                              └─────────────────┘
                                                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AWS Polly     │    │   AWS Textract  │    │   S3 Buckets    │
│                 │◀───│                 │◀───│                 │
│ - Text to Speech│    │ - OCR Processing│    │ - Images        │
│ - Neural Voices │    │ - Text Extraction│   │ - Audio Files   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Workflow

1. **Upload**: User uploads an image through the React frontend
2. **Storage**: Image is stored in S3 images bucket via presigned URL
3. **Trigger**: S3 event automatically triggers the text extraction Lambda
4. **OCR**: AWS Textract extracts text from the uploaded image
5. **Speech**: AWS Polly converts extracted text to MP3 audio
6. **Storage**: Generated audio is saved to S3 audio bucket
7. **Retrieval**: Frontend fetches the generated audio file for playback

## 🚀 Tech Stack

### Frontend

- **React 19** with TypeScript
- **Vite** for fast development and building
- **TailwindCSS** for styling
- **Axios** for API communication
- **AWS SDK** for S3 operations

### Backend

- **AWS Lambda** (Python 3.12) for serverless compute
- **AWS API Gateway** for REST API endpoints
- **AWS S3** for file storage
- **AWS Textract** for OCR text extraction
- **AWS Polly** for text-to-speech conversion
- **AWS IAM** for security and permissions

### Infrastructure

- **Terraform** for Infrastructure as Code
- **S3 Event Notifications** for automated processing
- **Lambda Layers** for shared dependencies

## 📋 Prerequisites

- AWS Account with appropriate permissions
- Terraform 
- Node.js >= 18
- npm or yarn package manager

## 🛠️ Installation & Deployment

### 1. Clone the Repository

```bash
git clone <repository-url>
cd audio-notes-project
```

### 2. Deploy AWS Infrastructure

```bash
cd audo-notes-infra

# Initialize Terraform
terraform init

# Review the deployment plan
terraform plan

# Deploy infrastructure
terraform apply
```


## ⚙️ Configuration

### Environment Variables

The Lambda functions use the following environment variables (automatically configured by Terraform):

- `IMAGES_BUCKET`: S3 bucket for storing uploaded images
- `AUDIO_BUCKET`: S3 bucket for storing generated audio files

### Customizable Settings

In `variables.tf`, you can customize:

```terraform
variable "audio-bucket-name" {
  description = "Name of the S3 bucket for audio files"
  default     = "your-unique-audio-bucket-name"
}

variable "images-bucket-name" {
  description = "Name of the S3 bucket for images"
  default     = "your-unique-images-bucket-name"
}
```

## 🎵 Supported Formats

### Input Images

- JPEG (.jpg, .jpeg)
- PNG (.png)
- WebP (.webp)

### Output Audio

- MP3 format
- Neural voice (Joanna) for high-quality speech
- Configurable voice options in Lambda function

## 💰 Cost Considerations & Trade-offs

### AWS Service Costs

- **Lambda**: Pay per execution (~$0.0000166667 per GB-second)
- **S3**: Storage and transfer costs (~$0.023 per GB/month)
- **Textract**: $1.50 per 1,000 pages for text detection
- **Polly**: $4.00 per 1 million characters for Neural voices
- **API Gateway**: $3.50 per million API calls

### Trade-offs Made

#### 1. **Simplicity vs. Scalability**

- **Chosen**: Simple S3 event-driven architecture
- **Trade-off**: Manual polling for audio status instead of real-time WebSocket updates
- **Rationale**: Reduces complexity and cost for MVP, suitable for moderate usage

#### 2. **Cost vs. Quality**

- **Chosen**: AWS Polly Neural voices
- **Trade-off**: Higher cost (~4x) compared to standard voices
- **Rationale**: Significantly better audio quality justifies the cost

#### 3. **Processing Speed vs. Cost**

- **Chosen**: On-demand Lambda processing
- **Trade-off**: Cold start latency vs. keeping instances warm
- **Rationale**: Cost-effective for sporadic usage patterns

#### 4. **Storage vs. Processing**

- **Chosen**: Store both images and audio files
- **Trade-off**: Higher storage costs vs. regenerating audio on demand
- **Rationale**: Better user experience with instant audio playback

#### 5. **Security vs. Convenience**

- **Chosen**: Presigned URLs for S3 uploads
- **Trade-off**: Some security considerations vs. direct Lambda uploads
- **Rationale**: Reduces Lambda execution time and costs

## 🔧 Development

### Local Development

```bash
# Frontend development
cd audio-notes-client
npm run dev

# Infrastructure changes
cd audo-notes-infra
terraform plan
terraform apply
```

### Testing

```bash
# Run frontend tests
npm test

# Lint code
npm run lint
```

## 📈 Performance Metrics

- **Text Extraction**: ~2-5 seconds per image
- **Audio Generation**: ~1-3 seconds per 100 words
- **Total Processing**: ~5-10 seconds for typical documents
- **Cold Start**: ~1-2 seconds for Lambda initialization

## 🔮 Future Enhancements

- [ ] **Real-time Processing Status**: WebSocket integration for live updates
- [ ] **Batch Processing**: Support for multiple image uploads
- [ ] **Voice Selection**: User-selectable voice options
- [ ] **Text Editing**: Allow users to edit extracted text before audio generation
- [ ] **Audio Settings**: Speed, pitch, and volume controls
- [ ] **File Management**: History and organization of processed files
- [ ] **Mobile App**: React Native application
- [ ] **Multi-language Support**: OCR and TTS in multiple languages

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request


---

**Author**: [Your Name]  
**Portfolio**: [Your Portfolio URL]  
**LinkedIn**: [Your LinkedIn URL]
