# ReachyAI: AI-Powered Multilingual Voice Health Platform

## Project Overview

ReachyAI is a multi-lingual health platform enabling patients to describe their ailments via voice in their local African dialects (Twi, Ga,etc). Doctors receive and manage cases efficiently using voice and AI-assisted services.

- **Goal:** Voice-first, accessible healthcare for underserved populations, leveraging AI for both patients and doctors.
- **Innovation:** Multilingual voice support, offline sync, doctor-patient flows, and AI-powered triage—all built for compliance and mobile-first experiences.

---

## Core Features & Technical Highlights

- **Voice AI Stack**
    - AWS Transcribe (speech-to-text, Twi/Ga/English)
    - AWS Polly (text-to-speech)
    - HuggingFace for training and inference
- **AI Workflows**
    - Real-time voice symptom capture and transcription
    - Doctor triage & response, voice transcription/translation
    - Automatic language detection and translation for cases
- **Offline & Security**
    - Stores recordings locally if offline, auto-syncs with the cloud
    - HIPAA/GDPR ready: encrypted storage, anonymization, audit logs

---

## Architecture

- **Frontend:** Angular (PWA), voice-first UI, TailwindCSS
- **Backend:** FastAPI, PostgreSQL, SQLAlchemy, AWS S3
- **Planned AWS Usage:** Transcribe, Polly, S3, (future: Comprehend Medical)

**Sample File Structure:**
```
reachy-angular/src/app/
├── pages/
│   ├── landing.page.ts/html/css
│   ├── patient/
│   ├── doctor/
├── components/
│   ├── voice-input.component.ts/html/css
│   ├── language-switcher.component.ts/html/css
│   ├── transcription-display.component.ts/html/css
│   ├── audio-player.component.ts/html/css
├── services/
│   ├── voice-recognition.service.ts
│   ├── translation.service.ts
│   ├── consultation.service.ts
```

---

## Current Status

- **Voice UI, dashboards, backend CRUD APIs, S3 upload:** Core complete
- **In Progress:** Full AWS AI/voice integration, multi-language enhancements

---

## API Excerpts (Endpoints)

```
POST /api/v1/voice/transcribe   # AWS Transcribe integration
POST /api/v1/voice/translate    # HuggingFace translation
POST /api/v1/voice/synthesize   # AWS Polly TTS
POST /api/v1/consultations      # Patient/doctor consult flow
```

**Consultation Model:**
- id, patient_id, doctor_id, audio_url, transcription, language, created_at, status

---

## Support Needs from AWS

- Guidance and support for scaling AWS Transcribe, Polly for local African languages
- Compliance consulting (PII/PHI, encryption at rest/in transit)
- Startup credits for AI/ML evaluation and ramping workload

---

## Mac M1/M2 (Apple Silicon) Setup

### PyTorch with MPS Support
The transcription service automatically detects and uses Apple's Metal Performance Shaders (MPS) on Mac M1/M2 for faster inference.

**Installation:**
```bash
# Make sure you have PyTorch with MPS support
pip install torch torchaudio transformers
```

The service will automatically:
- Detect MPS availability
- Use MPS backend for faster transcription (faster than CPU)
- Fall back to CPU if MPS is not available or if certain operations require it

**Performance Notes:**
- MPS is significantly faster than CPU for model inference
- Some operations in Whisper may still use CPU (this is normal)
- First transcription will be slower as the model downloads from Hugging Face

**Environment Variables (Optional):**
- `WHISPER_DEVICE`: Set to `'mps'` to force MPS, `'cpu'` for CPU, or leave unset for auto-detect
- `WHISPER_MODEL`: Override the default model (defaults to `teckedd/whisper-small-serlabs-twi-asr`)

---

*For more details, see `PLATFORM_SPECIFICATION.md` and internal documentation.*

---

## Cloud Infrastructure and AI Roadmap

### S3 for Voice Data Storage
All user voice recordings and transcriptions are stored via AWS S3, providing durable, scalable, and secure storage with encryption and access control.
- **Development Phase:** Using **LocalStack** to emulate S3 for local and cost-free development.
- **Production Plan:** All storage endpoints will migrate to **live AWS S3**, with encryption-at-rest, lifecycle management, and AWS IAM integration for compliance (HIPAA/GDPR).

### EC2 Usage
- **Backend Hosting:** FastAPI backend services are containerized and will be deployed on EC2 instances for scalable compute.
- **API & AI Workloads:** EC2/ECS/Fargate will handle backend, API traffic, and AI inference/media conversion workloads, leveraging scalable instance types per demand.
- **Request:** Guidance and recommendations for secure, cost-efficient deployment, scaling, and monitoring in production, especially for AI health workloads.

### AI Training & Modeling: SageMaker Needs
- **Current Status:** Multilingual ASR (Whisper model fine-tuning for Twi, Ga, English) is prototyped and tuned on **Kaggle Kernels** due to resource constraints.
- **Limitation:** Kaggle lacks production-ready, compliant, scalable infrastructure.
- **Target:** **Amazon SageMaker** will be used for secure GPU training at scale, managed endpoint hosting, larger model/inference experiments, and HIPAA-aligned development.
- **Request:** AWS onboarding, credits, and support to migrate model fine-tuning/inference pipelines to SageMaker; advice for productionizing open-source ASR with compliance.

**Resource/Support Summary:**
- S3 (LocalStack → AWS S3) for encrypted, compliant storage of health voice data
- EC2 for scalable backend/AI compute, needs best practices for production scale
- SageMaker for end-to-end ASR model lifecycle, request onboarding and credits
- Security/storage best practices for voice health data & HIPAA/PII pipeline review

---
