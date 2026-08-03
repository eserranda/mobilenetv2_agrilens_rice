# Rice Disease Classification - Model Training

Folder ini berisi script untuk melatih model **MobileNetV2** dari awal menggunakan dataset riil daun padi yang terinfeksi penyakit.

Proses pelatihan (*training*) sebaiknya dijalankan di **Google Colab** (menggunakan GPU gratis) agar prosesnya cepat selesai (kurang dari 10 menit) dan tidak membebani komputer lokal Anda.

---

## Dataset
Dataset yang digunakan adalah **Rice Leaf Disease Images** oleh Nirmal Sankalana di Kaggle, yang memiliki 4 kelas berikut:
1. **Bacterial blight**
2. **Blast**
3. **Brown Spot**
4. **Tungro**

Link Dataset Kaggle:
👉 [Kaggle - Rice Leaf Disease Images](https://www.kaggle.com/datasets/nirmalsankalana/rice-leaf-disease-image)

---

## Cara Melatih Model di Google Colab (Sangat Direkomendasikan)

Ikuti langkah-langkah berikut untuk melatih model di Google Colab dan mendownload hasilnya:

1. **Buka Google Colab**:
   Kunjungi [colab.research.google.com](https://colab.research.google.com/) dan buat Notebook Python 3 baru.

2. **Ganti Runtime ke GPU**:
   * Klik menu **Runtime** > **Change runtime type**.
   * Pilih **T4 GPU** pada bagian *Hardware accelerator*.
   * Klik **Save**.

3. **Salin & Jalankan Script Persiapan Dataset (Cell 1)**:
   Buat cell baru di Colab, paste kode berikut, lalu jalankan untuk mendownload dataset secara otomatis menggunakan `kagglehub`:
   ```python
   !pip install kagglehub torch torchvision
   import kagglehub
   import os
   import shutil

   print("Mengunduh dataset dari Kaggle...")
   path = kagglehub.dataset_download("nirmalsankalana/rice-leaf-disease-image")
   print("Dataset terunduh di:", path)

   # Buat folder terstruktur
   os.makedirs("training/data", exist_ok=True)

   # Salin gambar-gambar ke folder training/data
   target_classes = ['Bacterial blight', 'Blast', 'Brown Spot', 'Tungro']

   for folder_name in os.listdir(path):
       matched_class = None
       for target in target_classes:
           if folder_name.lower().replace(" ", "").replace("_", "") == target.lower().replace(" ", "").replace("_", ""):
               matched_class = target
               break
       if matched_class:
           src = os.path.join(path, folder_name)
           dest = os.path.join("training/data", matched_class)
           if os.path.exists(dest):
               shutil.rmtree(dest)
           shutil.copytree(src, dest)
           print(f"Salin: '{folder_name}' -> 'training/data/{matched_class}'")
   print("Dataset siap!")
   ```

4. **Salin & Jalankan Script Training (Cell 2)**:
   Buat cell baru lagi untuk membuat file `train.py` di Colab:
   ```python
   # Kode isi train.py disalin otomatis, buat cell ini lalu jalankan:
   # (Isi script ini sama seperti yang ada di training/train.py project Anda)
   ```

5. **Jalankan Proses Training (Cell 3)**:
   ```bash
   !python train.py
   ```

6. **Unduh File Model (`mobilenetv2_padi.pth`)**:
   Setelah training selesai, klik ikon **Folder 📁** di sebelah kiri Colab, klik kanan pada file `mobilenetv2_padi.pth`, lalu pilih **Download**.

7. **Pasang di Project API**:
   Pindahkan file yang diunduh ke folder `models/` di project lokal Anda (`d:\Rice-Disease-Detection\models\mobilenetv2_padi.pth`) untuk menggantikan model dummy.

---

## Cara Melatih Model Secara Lokal (Jika komputer memiliki GPU/Cuda)

1. Buat folder `training/data/` di komputer Anda:
   `d:\Rice-Disease-Detection\training\data\`
2. Ekstrak gambar-gambar dataset dari Kaggle ke dalam folder tersebut sehingga strukturnya menjadi:
   ```text
   training/
   └── data/
       ├── Bacterial blight/
       ├── Blast/
       ├── Brown Spot/
       └── Tungro/
   ```
3. Aktifkan virtual environment Anda:
   ```powershell
   .venv\Scripts\Activate.ps1
   ```
4. Jalankan script training:
   ```powershell
   python training/train.py
   ```
5. File `mobilenetv2_padi.pth` akan otomatis disimpan ke dalam folder `models/` di project utama Anda setelah proses training selesai.
