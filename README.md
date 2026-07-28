# Rice Disease API 🌾

REST API untuk deteksi dini penyakit pada daun padi menggunakan model MobileNetV2 berbasis PyTorch.

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.4-red)](https://pytorch.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Deskripsi

Repository ini menyediakan backend inferensi berbasis FastAPI yang:
- Menerima gambar daun padi melalui REST API
- Memproses gambar menggunakan pipeline preprocessing standar MobileNetV2
- Menjalankan inferensi menggunakan model PyTorch hasil training di Google Colab
- Mengembalikan prediksi penyakit beserta confidence score

> ⚠️ Repository ini **tidak melakukan training model**. Training dilakukan di Google Colab dan model diekspor ke folder `models/`.

---

## 🏗️ Struktur Proyek

```
rice-disease-api/
├── app/
│   ├── main.py              # FastAPI app & lifespan
│   ├── config.py            # Settings via Pydantic BaseSettings
│   ├── api/v1/
│   │   ├── router.py
│   │   └── endpoints/
│   │       ├── health.py    # GET /api/v1/health
│   │       └── detection.py # POST /api/v1/detect
│   ├── core/
│   │   ├── vision/
│   │   │   ├── loader.py        # Model & artifact loader
│   │   │   ├── preprocessing.py # Image transforms
│   │   │   └── predictor.py     # Inference engine
│   │   └── llm/                 # Phase 2 - LLM integration
│   │       ├── engine.py
│   │       ├── prompt.py
│   │       └── cot.py
│   ├── schemas/
│   │   ├── health.py
│   │   └── detection.py
│   └── utils/
│       ├── exceptions.py
│       └── image_validator.py
├── models/
│   ├── mobilenetv2_padi.pth  # ← Taruh model terlatih di sini
│   ├── labels.json
│   └── metadata.json
├── scripts/
│   └── generate_sample_model.py
├── tests/
│   ├── test_health.py
│   ├── test_detection.py
│   └── test_vision.py
├── .env
├── .env.example
└── requirements.txt
```

---

## 🚀 Cara Menjalankan

### 1. Clone & Setup Environment

```bash
git clone <repo-url>
cd rice-disease-api
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/macOS
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Konfigurasi Environment

```bash
copy .env.example .env
# Edit .env sesuai kebutuhan
```

### 4. Generate Sample Model (Development)

Jika belum memiliki model terlatih, buat model dengan bobot acak untuk keperluan testing:

```bash
python scripts/generate_sample_model.py
```

> ⚠️ Model ini menggunakan **bobot acak** dan tidak menghasilkan prediksi yang akurat. Ganti dengan model terlatih dari Google Colab untuk produksi.

### 5. Jalankan Server

```bash
uvicorn app.main:app --reload
```

Server berjalan di: `http://localhost:8000`

---

## 📡 API Endpoints

### Health Check

```http
GET /api/v1/health
```

**Response:**
```json
{
    "status": "ok",
    "version": "1.0.0",
    "uptime_seconds": 123.45,
    "timestamp": "2024-01-01T00:00:00Z"
}
```

---

### Disease Detection

```http
POST /api/v1/detect
Content-Type: multipart/form-data
```

**Input:** `file` — gambar daun padi (JPG, JPEG, PNG, WebP, maks 10 MB)

**Response:**
```json
{
    "disease": "Brown Spot",
    "confidence": 0.9734,
    "inference_time_ms": 42.5,
    "metadata": {
        "model_name": "MobileNetV2",
        "num_classes": 4,
        "input_size": [224, 224]
    }
}
```

---

## 🧪 Menjalankan Tests

```bash
pytest tests/ -v
```

---

## 📁 Model Artifacts

| File | Deskripsi |
|------|-----------|
| `models/mobilenetv2_padi.pth` | Bobot model PyTorch (state dict) |
| `models/labels.json` | Mapping class index → nama penyakit |
| `models/metadata.json` | Metadata arsitektur dan training |

### Kelas Penyakit yang Didukung

| Index | Label |
|-------|-------|
| 0 | Brown Spot |
| 1 | Healthy |
| 2 | Hispa |
| 3 | Leaf Blast |

---

## 🔭 Roadmap

### Phase 1 (Current) ✅
- FastAPI Backend
- MobileNetV2 Inference
- Image Validation
- Health & Detection Endpoints

### Phase 2 (Planned)
- OpenAI Integration
- Chain-of-Thought Diagnosis Explanation
- Treatment Recommendation
- Severity Classification

---

## 📄 License

MIT License — lihat [LICENSE](LICENSE).


# Jalankan server FastAPI dengan auto-reload (untuk development)
.\.venv\Scripts\uvicorn app.main:app --reload
