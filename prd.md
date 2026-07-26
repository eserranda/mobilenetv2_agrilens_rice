# Product Requirements Document (PRD)

# Rice Disease API

Version: 1.0

Status: Draft

---

# 1. Overview

Rice Disease API adalah backend berbasis Python yang menyediakan layanan deteksi dini penyakit pada daun padi menggunakan model Artificial Intelligence berbasis MobileNetV2.

Repository ini **tidak melakukan proses training model**. Seluruh proses penelitian, preprocessing dataset, training, dan evaluasi dilakukan menggunakan Google Colab.

Model hasil training kemudian diekspor ke repository ini dan digunakan sebagai engine inferensi.

Repository ini dirancang agar pada tahap selanjutnya dapat diintegrasikan dengan Large Language Model (LLM) untuk menghasilkan penjelasan diagnosis menggunakan pendekatan Chain-of-Thought (CoT).

---

# 2. Objectives

Tujuan utama repository ini adalah:

* Menyediakan REST API untuk deteksi penyakit padi.
* Memuat model MobileNetV2 hasil training.
* Melakukan preprocessing gambar sebelum inferensi.
* Menghasilkan prediksi beserta confidence score.
* Menjadi fondasi integrasi AI Multimodal pada fase berikutnya.
* Memiliki arsitektur yang modular, bersih, dan mudah dikembangkan.

---

# 3. Target Users

Target pengguna API adalah:

* Peneliti
* Akademisi
* Mahasiswa
* Pengembang aplikasi pertanian
* Sistem informasi pertanian

---

# 4. Project Scope

## Included

* FastAPI Backend
* REST API
* Image Upload
* Image Preprocessing
* MobileNetV2 Inference
* Confidence Score
* Health Check Endpoint
* Model Loader
* JSON Response

## Excluded

* Model Training
* Dataset Management
* Hyperparameter Tuning
* Data Augmentation
* Model Evaluation
* User Authentication
* Database
* Dashboard

Semua proses di atas dilakukan di Google Colab dan bukan bagian dari repository ini.

---

# 5. Technology Stack

Programming Language

* Python 3.12+

Backend

* FastAPI

Machine Learning

* PyTorch
* TorchVision

Image Processing

* OpenCV
* Pillow

Validation

* Pydantic

Utilities

* NumPy

Future Integration

* OpenAI API

Development

* VS Code

---

# 6. System Architecture

```text
Client
    │
    ▼
REST API (FastAPI)
    │
    ▼
Image Validation
    │
    ▼
Vision Preprocessing
    │
    ▼
MobileNetV2 Predictor
    │
    ▼
Prediction
    │
    ▼
JSON Response
```

Future Architecture

```text
Client
    │
    ▼
REST API
    │
    ▼
Vision Module
    │
    ▼
Prediction
    │
    ▼
LLM Module
    │
    ▼
Chain-of-Thought
    │
    ▼
Diagnosis Explanation
    │
    ▼
JSON Response
```

---

# 7. Model Lifecycle

Model MobileNetV2 dihasilkan melalui proses berikut:

```text
Dataset

↓

Google Colab

↓

Image Preprocessing

↓

Training

↓

Evaluation

↓

Export Model (.pth)

↓

Copy ke folder models/

↓

Rice Disease API

↓

Inference
```

Repository ini hanya menggunakan model yang telah selesai dilatih.

---

# 8. Project Structure

```text
rice-disease-api/

├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py
│   │       └── endpoints/
│   │           ├── health.py
│   │           └── detection.py
│   │
│   ├── core/
│   │   ├── vision/
│   │   │   ├── loader.py
│   │   │   ├── predictor.py
│   │   │.py
│   │   │
│   │   └── llm/
│   │       ├── engine.py
│   │       ├── prompt.py
│   │       └── cot.py
│   │
│   ├── schemas/
│   │   ├── detection.py
│   │   └── health.py
│   │
│   └── utils/
│
├── models/
│   ├── mobilenetv2_padi.pth
│   ├── labels.json
│   └── metadata.json
│
├── .env
├── .gitignore
├── requirements.txt
├── README.md
└── LICENSE
```

---

# 9. Folder Responsibilities

## app/

Berisi seluruh source code aplikasi.

---

## api/

Berisi seluruh REST API.

Endpoint hanya bertugas:

* menerima request
* melakukan validasi
* memanggil business logic
* mengembalikan response

Endpoint tidak boleh memiliki logika AI.

---

## core/

Berisi seluruh business logic Artificial Intelligence.

Core tidak boleh mengetahui implementasi HTTP maupun FastAPI.

Core dibagi menjadi dua domain utama.

### Vision

Bertanggung jawab terhadap Computer Vision.

### LLM

Bertanggung jawab terhadap penjelasan hasil prediksi.

---

# 10. Vision Module

Folder:

```text
app/core/vision/
```

## loader.py

Bertanggung jawab untuk:

* memuat model MobileNetV2
* memuat label klasifikasi
* memuat metadata model
* memilih device (CPU/GPU)

Output:

Model siap digunakan.

---

## preprocessing.py

Bertanggung jawab untuk:

* resize image
* normalize
* convert image
* tensor conversion

Output:

Tensor siap diprediksi.

---

## predictor.py

Bertanggung jawab untuk:

* menjalankan preprocessing
* melakukan inferensi
* menghitung confidence score

Output:

```json
{
    "disease": "Brown Spot",
    "confidence": 0.9734
}
```

Predictor tidak mengetahui keberadaan LLM.

---

# 11. LLM Module

Folder:

```text
app/core/llm/
```

Module ini belum digunakan pada Phase 1 namun telah dipersiapkan untuk pengembangan berikutnya.

## engine.py

Mengelola komunikasi dengan provider LLM.

Contoh:

* OpenAI

---

## prompt.py

Berisi seluruh Prompt Template.

Prompt tidak boleh ditulis langsung di source code lain.

---

## cot.py

Mengubah hasil klasifikasi menjadi penjelasan diagnosis menggunakan metode Chain-of-Thought.

Input:

* prediction
* confidence

Output:

* explanation
* recommendation

---

# 12. Models

Folder:

```text
models/
```

Berisi seluruh artefak hasil training.

Contoh:

```text
mobilenetv2_padi.pth
labels.json
metadata.json
```

Folder ini tidak boleh berisi dataset.

---

# 13. API Endpoints

## Health Check

```
GET /api/v1/health
```

Response:

* status
* version
* uptime

---

## Disease Detection

```
POST /api/v1/detect
```

Input:

* image

Output:

* predicted disease
* confidence score

---

# 14. Future Features

Phase berikutnya akan menambahkan:

* OpenAI Integration
* Chain-of-Thought
* Human-readable Diagnosis
* Disease Recommendation
* Suggested Treatment
* Confidence Explanation

---

# 15. Coding Standards

Seluruh source code wajib mengikuti prinsip berikut:

* Clean Architecture
* Modular Design
* Separation of Concerns
* Single Responsibility Principle
* DRY (Don't Repeat Yourself)
* Type Hint untuk seluruh fungsi baru
* Tidak ada hardcoded configuration
* Prompt dipisahkan dari business logic
* Endpoint tidak boleh berisi AI logic
* Vision Module tidak boleh mengetahui implementasi LLM
* LLM Module tidak boleh melakukan inferensi gambar

---

# 16. Success Criteria

Repository dianggap memenuhi target apabila:

* FastAPI berhasil dijalankan.
* Health endpoint berjalan dengan baik.
* Detection endpoint menerima gambar dengan valid.
* MobileNetV2 berhasil dimuat.
* Gambar berhasil diproses sebelum inferensi.
* API mengembalikan prediksi beserta confidence score.
* Struktur aplikasi siap menerima integrasi OpenAI tanpa perubahan arsitektur yang signifikan.
