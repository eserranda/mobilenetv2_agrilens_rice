# Panduan Skripsi: Implementasi Chain-of-Thought pada Sistem Multimodal MobileNetV2

Dokumen ini disusun khusus sebagai bahan belajar untuk persiapan sidang skripsi dengan judul:
**"IMPLEMENTASI CHAIN-OF-THOUGHT PADA SISTEM MULTIMODAL MOBILENETV2 UNTUK DETEKSI DINI PENYAKIT PADI"**

---

## 📑 1. Konsep Utama & Definisi Judul

Jika dosen penguji menanyakan makna dari istilah-istilah di judul skripsi Anda, berikut penjelasan akademisnya:

### A. Kenapa disebut "Sistem Multimodal"?
Sistem disebut **Multimodal** karena mengolah dan menggabungkan lebih dari satu jenis (modalitas) data. 
* **Modalitas 1 (Visual)**: Gambar daun padi diolah oleh model Convolutional Neural Network (CNN) yaitu **MobileNetV2**.
* **Modalitas 2 (Tekstual)**: Bahasa alami diolah oleh Large Language Model (LLM) OpenAI GPT melalui instruksi **Chain-of-Thought**.
* **Integrasi**: Prediksi kelas visual dan tingkat keyakinan (confidence) dari model visi digunakan sebagai *context input* untuk menstimulasi penalaran di model teks.

### B. Kenapa menggunakan "MobileNetV2"?
* **MobileNetV2** adalah arsitektur CNN ringan yang dirancang khusus untuk perangkat mobile atau komputer berspesifikasi rendah (*edge devices*).
* Menggunakan teknik **Inverted Residuals** dan **Linear Bottlenecks** yang meminimalkan jumlah parameter namun tetap menjaga akurasi tinggi.
* **Relevansi Penelitian**: Sangat efisien untuk klasifikasi gambar daun padi secara real-time pada lingkungan pertanian yang memiliki keterbatasan daya komputasi.

### C. Apa itu "Chain-of-Thought (CoT)"?
* **Chain-of-Thought** adalah metode rekayasa prompt (*prompt engineering*) yang memaksa Large Language Model (LLM) untuk menghasilkan serangkaian langkah penalaran logis sebelum memberikan kesimpulan akhir.
* Alih-alih langsung memberikan rekomendasi secara instan, AI diminta untuk menganalisis karakteristik visual penyakit, risiko penyebaran, serta menganalisis kepastian akurasi deteksi model visi terlebih dahulu.

---

## 📂 2. Pemetaan Logic Chain-of-Thought di Kode Program

Apabila dosen meminta Anda menunjukkan file kode program yang mengurusi logika Chain-of-Thought, berikut adalah daftarnya:

### 1. File Instruksi CoT (Prompt Engineering)
* **Lokasi File**: [app/core/llm/prompt.py](app/core/llm/prompt.py)
* **Penjelasan**: File ini mendefinisikan template prompt (`DIAGNOSIS_COT`). Di dalamnya terdapat perintah tegas bagi model LLM untuk merumuskan proses berpikirnya terlebih dahulu di kolom `"thinking"` sebelum mengisi kolom `"explanation"` dan `"recommendation"` dalam Bahasa Indonesia.

### 2. File Pemroses & Parser CoT
* **Lokasi File**: [app/core/llm/cot.py](app/core/llm/cot.py)
* **Penjelasan**: Berisi class `ChainOfThoughtExplainer` yang memanggil LLM engine, memformat prompt dengan variabel dinamis (nama penyakit dan confidence score), serta mengurai output JSON menjadi objek data Python (`DiagnosisExplanation`).

### 3. File Jembatan Multimodal (Endpoint API)
* **Lokasi File**: [app/api/v1/endpoints/detection.py](app/api/v1/endpoints/detection.py)
* **Penjelasan**: Method `detect_disease()` menjembatani model visi dan teks.
  - Baris 83: Model visi memprediksi penyakit daun padi (`predictor.predict(image)`).
  - Baris 100: Hasil prediksi dan confidence dikirim ke model teks untuk dianalisis secara CoT (`explainer.explain(...)`).

### 4. File Engine Konektivitas LLM
* **Lokasi File**: [app/core/llm/engine.py](app/core/llm/engine.py)
* **Penjelasan**: Mengurus komunikasi dengan API OpenAI menggunakan SDK resmi (`OpenAI.chat.completions.create`) dengan mode respon JSON (`json_object`).

---

## 🗺️ 3. Diagram Alur Sistem (Multimodal Pipeline)

Berikut adalah visualisasi alur data dari gambar daun hingga menghasilkan output CoT:

```text
[ Input Gambar Daun Padi ]
          │
          ▼
┌─────────────────────────────────┐
│       1. MODALITAS VISI         │
│         (MobileNetV2)           │
└────────────────┬────────────────┘
                 │
                 ▼ (Hasil Prediksi: e.g. "Bacterial blight", Conf: 92%)
┌─────────────────────────────────┐
│     Jembatan API Multimodal     │  <--- Menyuntikkan hasil visi ke Prompt
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│       2. MODALITAS BAHASA       │
│      (LLM + Prompt CoT)         │
└────────────────┬────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────┐
│               3. OUTPUT TERSTRUKTUR (JSON)             │
│  - Thinking       : Analisis gejala visual & akurasi   │ (Proses CoT)
│  - Explanation    : Penjelasan penyakit daun           │
│  - Recommendation : Tindakan penanganan petani          │
│  - Severity       : Tingkat keparahan                  │
└────────────────────────────────────────────────────────┘
```

---

## 💬 4. Simulasi Tanya-Jawab Sidang Skripsi

### Pertanyaan 1: "Bagaimana cara Anda memvalidasi bahwa proses Chain-of-Thought benar-benar terjadi dan bukan sekadar mengambil teks template?"
* **Jawaban**: 
  > *"Proses CoT terbukti aktif secara dinamis melalui kolom respon `thinking`. Di kolom tersebut, LLM melakukan penalaran real-time berdasarkan input dinamis yang kami berikan. Sebagai contoh, jika confidence model visi bernilai 70%, LLM akan menganalisis di kolom `thinking` bahwa tingkat kepastiannya sedang (*moderate*) dan ada risiko kesalahan deteksi. Namun, jika confidence bernilai 99%, LLM akan menalar bahwa deteksi tersebut sangat valid dan menyarankan tindakan langsung dengan keyakinan penuh. Semua ini dirumuskan dinamis tanpa template statis."*

### Pertanyaan 2: "Mengapa Anda memilih membagi sistem menjadi MobileNetV2 lokal dan LLM cloud (OpenAI), tidak menggunakan model multimodal end-to-end yang besar?"
* **Jawaban**: 
  > *"Pertimbangannya adalah efisiensi sumber daya (*computational cost*) dan portabilitas. Model visi MobileNetV2 berukuran sangat kecil (hanya sekitar 8.7 MB) dan dapat berjalan secara lokal di perangkat edge dengan sangat cepat (di bawah 50 ms) tanpa GPU mahal. Sementara LLM besar yang bertugas melakukan penalaran (CoT) diletakkan di cloud (via API), sehingga sistem tetap ringan namun memiliki kemampuan diagnosis setingkat ahli agronomi tanpa membebani server lokal pertanian."*

### Pertanyaan 3: "Bagaimana jika koneksi internet terputus? Apakah sistem Anda akan lumpuh total?"
* **Jawaban**: 
  > *"Tidak. Sistem kami dirancang dengan prinsip ketahanan (*graceful degradation/fallback*). Jika koneksi ke OpenAI API terputus atau terjadi kegagalan pemanggilan LLM, sistem penanganan error (pada file `detection.py` baris 105-111) akan secara otomatis menangkap error tersebut. Sistem akan tetap mengembalikan hasil deteksi penyakit dari MobileNetV2 lokal, sementara penjelasan teks CoT akan digantikan dengan pesan fallback default. Dengan begitu, petani tetap mendapatkan prediksi penyakit daunnya meskipun internet sedang bermasalah."*
