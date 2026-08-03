"""
training/train.py
==================
Script untuk melatih model MobileNetV2 untuk mengklasifikasikan penyakit daun padi.
Mendukung 4 kelas: 'Bacterial_Blight', 'Blast', 'Brown_Spot', 'Healthy'.

================================================================================
PETUNJUK PENGGUNAAN DI GOOGLE COLAB (BACA SEBELUM SALIN):
================================================================================
1. Buka Google Colab (https://colab.research.google.com).
2. Buat Notebook baru dan ubah tipe runtime ke GPU:
   - Pilih menu: Runtime -> Change runtime type -> Hardware accelerator -> T4 GPU.
3. Salin seluruh isi kode file ini dan tempelkan (paste) ke dalam satu sel kode di Colab.
4. Pastikan file dataset ZIP Anda sudah diunggah ke Google Drive.
5. Sesuaikan variabel di bawah (baris 45) jika lokasi file ZIP Anda di Google Drive berbeda:
   - ZIP_PATH_ON_DRIVE = "/content/drive/MyDrive/dataset.zip" (atau nama file ZIP Anda)
6. Jalankan sel kode tersebut. Script akan otomatis:
   - Menghubungkan ke Google Drive Anda.
   - Mengekstrak file dataset ke direktori lokal Colab agar training berjalan sangat cepat.
   - Menjalankan training memanfaatkan GPU T4.
   - Menyimpan model terbaik ke Google Drive atau direktori Colab.
7. Setelah selesai, unduh file model "mobilenetv2_padi.pth" hasil training dan masukkan ke folder:
   - D:\Rice-Disease-Detection\backend\app\models\mobilenetv2_padi.pth
================================================================================
"""

import os
import sys
import time
import zipfile
import copy
from pathlib import Path
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms, models

# --- KONFIGURASI GOOGLE DRIVE (Ubah di sini jika diperlukan) ---
ZIP_PATH_ON_DRIVE = "/content/drive/MyDrive/dataset.zip" # Lokasi ZIP dataset di Google Drive Anda
EXTRACT_DIRECTORY = "/content/dataset"                  # Lokasi ekstraksi sementara di Colab

# --- KELAS & LABEL YANG DIGUNAKAN ---
# Sesuai dengan label di models/labels.json
CLASS_LABELS = ["Bacterial_Blight", "Blast", "Brown_Spot", "Healthy"]
NUM_CLASSES = len(CLASS_LABELS)


def check_and_setup_colab():
    """Mendeteksi apakah script berjalan di Google Colab dan melakukan auto-mount & unzip."""
    in_colab = "google.colab" in sys.modules
    
    if not in_colab:
        print("[INFO] Berjalan di lingkungan lokal (Bukan Google Colab).")
        return "training/data"
        
    print("[INFO] Terdeteksi berjalan di Google Colab. Menyiapkan Google Drive...")
    from google.colab import drive
    
    # Mount Google Drive
    if not os.path.exists("/content/drive"):
        drive.mount("/content/drive")
        
    # Periksa ketersediaan file ZIP
    if not os.path.exists(ZIP_PATH_ON_DRIVE):
        print(f"[ERROR] File dataset ZIP tidak ditemukan di Drive: '{ZIP_PATH_ON_DRIVE}'")
        print("Silakan periksa nama file dan pastikan file sudah diunggah ke Google Drive Anda.")
        sys.exit(1)
        
    # Ekstrak file ZIP ke Colab lokal (lebih cepat dibaca saat training dibanding membaca dari Drive langsung)
    if not os.path.exists(EXTRACT_DIRECTORY):
        print(f"Mengekstrak dataset dari '{ZIP_PATH_ON_DRIVE}' ke '{EXTRACT_DIRECTORY}'...")
        os.makedirs(EXTRACT_DIRECTORY, exist_ok=True)
        with zipfile.ZipFile(ZIP_PATH_ON_DRIVE, 'r') as zip_ref:
            zip_ref.extractall(EXTRACT_DIRECTORY)
        print("Ekstraksi selesai.")
    else:
        print(f"Dataset sudah diekstrak di '{EXTRACT_DIRECTORY}'.")
        
    # Cari subfolder dataset di dalam direktori ekstraksi
    # Menangani jika file ZIP membungkus folder utama terlebih dahulu
    extracted_path = Path(EXTRACT_DIRECTORY)
    subdirs = [x for x in extracted_path.iterdir() if x.is_dir()]
    
    # Jika hanya ada 1 subfolder (misalnya 'dataset/' atau nama zip), gunakan subfolder itu
    if len(subdirs) == 1:
        return str(subdirs[0])
        
    return EXTRACT_DIRECTORY


def train_model(
    data_dir: str, 
    output_model_path: str = "mobilenetv2_padi.pth", 
    epochs: int = 15, 
    batch_size: int = 32, 
    learning_rate: float = 0.001
):
    """Melatih model MobileNetV2 menggunakan PyTorch."""
    print("==================================================")
    print("Memulai Proses Training Rice Disease Classification")
    print("==================================================")
    
    # 1. Menentukan Device (GPU jika tersedia)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"Device yang digunakan untuk training: {device}")
    if device.type == 'cuda':
        print(f"Nama GPU: {torch.cuda.get_device_name(0)}")

    # 2. Preprocessing & Augmentasi Gambar
    data_transforms = {
        'train': transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomVerticalFlip(),
            transforms.RandomRotation(20),
            transforms.ColorJitter(brightness=0.15, contrast=0.15, saturation=0.1),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
        'val': transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
    }

    # 3. Load Dataset dari Folder
    print(f"Membaca dataset dari direktori: {data_dir}")
    if not os.path.exists(data_dir):
        print(f"[ERROR] Direktori dataset tidak ditemukan: {data_dir}")
        return
        
    full_dataset = datasets.ImageFolder(root=data_dir)
    
    # Periksa kecocokan jumlah kelas folder
    if len(full_dataset.classes) != NUM_CLASSES:
        print(f"\n[PERINGATAN] Jumlah kelas terdeteksi ({len(full_dataset.classes)}) berbeda dengan target ({NUM_CLASSES})!")
        print(f"Kelas terdeteksi di folder: {full_dataset.classes}")
        print(f"Target kelas konfigurasi: {CLASS_LABELS}")

    # Membagi dataset menjadi 80% Training dan 20% Validasi
    train_size = int(0.8 * len(full_dataset))
    val_size = len(full_dataset) - train_size
    
    train_subset, val_subset = random_split(
        full_dataset, 
        [train_size, val_size], 
        generator=torch.Generator().manual_seed(42)
    )

    # Wrapper dataset untuk mengaplikasikan transformasi dinamis
    class TransformDataset(torch.utils.data.Dataset):
        def __init__(self, subset, transform):
            self.subset = subset
            self.transform = transform
        def __getitem__(self, index):
            x, y = self.subset[index]
            if self.transform:
                x = self.transform(x)
            return x, y
        def __len__(self):
            return len(self.subset)

    train_dataset = TransformDataset(train_subset, data_transforms['train'])
    val_dataset = TransformDataset(val_subset, data_transforms['val'])

    # 4. Membuat Data Loader
    # Gunakan num_workers > 0 di Colab/Linux untuk mempercepat loading data
    num_workers = 2 if "google.colab" in sys.modules else 0
    dataloaders = {
        'train': DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers, pin_memory=True),
        'val': DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers, pin_memory=True)
    }
    
    dataset_sizes = {
        'train': len(train_dataset),
        'val': len(val_dataset)
    }

    print(f"Total gambar training: {dataset_sizes['train']}")
    print(f"Total gambar validasi: {dataset_sizes['val']}")

    # 5. Inisialisasi Model MobileNetV2 pre-trained
    print("Mendownload model dasar MobileNetV2 pre-trained...")
    try:
        model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
    except AttributeError:
        model = models.mobilenet_v2(pretrained=True)

    # Bekukan bobot feature extractor agar tidak berubah di epoch-epoch awal
    for param in model.parameters():
        param.requires_grad = False

    # Ganti classification layer terakhir dengan jumlah kelas target (4 kelas)
    num_ftrs = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(num_ftrs, NUM_CLASSES)
    
    model = model.to(device)

    # 6. Menentukan Loss Function dan Optimizer
    criterion = nn.CrossEntropyLoss()
    
    # Hanya latih parameter di classification layer (classifier[1])
    optimizer = optim.Adam(model.classifier[1].parameters(), lr=learning_rate)

    # 7. Loop Training
    since = time.time()
    best_model_wts = copy.deepcopy(model.state_dict())
    best_acc = 0.0

    for epoch in range(epochs):
        print(f"\nEpoch {epoch+1}/{epochs}")
        print("-" * 10)

        for phase in ['train', 'val']:
            if phase == 'train':
                model.train()
            else:
                model.eval()

            running_loss = 0.0
            running_corrects = 0

            for inputs, labels in dataloaders[phase]:
                inputs = inputs.to(device)
                labels = labels.to(device)

                optimizer.zero_grad()

                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)

                    if phase == 'train':
                        loss.backward()
                        optimizer.step()

                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)

            epoch_loss = running_loss / dataset_sizes[phase]
            epoch_acc = running_corrects.double() / dataset_sizes[phase]

            print(f"{phase.capitalize()} Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}")

            if phase == 'val' and epoch_acc > best_acc:
                best_acc = epoch_acc
                best_model_wts = copy.deepcopy(model.state_dict())

    time_elapsed = time.time() - since
    print(f"\nTraining selesai dalam {time_elapsed // 60:.0f}m {time_elapsed % 60:.0f}s")
    print(f"Akurasi Validasi Terbaik: {best_acc:.4f}")

    # 8. Memuat bobot model terbaik dan menyimpannya ke disk
    model.load_state_dict(best_model_wts)
    
    output_path = Path(output_model_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    torch.save(model.state_dict(), output_path)
    print(f"[SUCCESS] Model terbaik berhasil disimpan ke: {output_path.resolve()}")
    print("==================================================")
    
    # Jika di Colab, tawarkan salinan langsung ke Google Drive agar model tidak hilang saat runtime reset
    if "google.colab" in sys.modules:
        drive_output_path = "/content/drive/MyDrive/mobilenetv2_padi.pth"
        try:
            import shutil
            shutil.copy(output_path, drive_output_path)
            print(f"[INFO] Salinan model juga dicadangkan ke Google Drive Anda: '{drive_output_path}'")
        except Exception as e:
            print(f"[WARN] Gagal menyalin model ke Google Drive: {e}")


if __name__ == "__main__":
    # Menyiapkan lokasi dataset secara cerdas (lokal vs Colab)
    DATASET_PATH = check_and_setup_colab()
    
    # Jalankan training
    # Output model akan disimpan lokal sebagai 'mobilenetv2_padi.pth'
    train_model(
        data_dir=DATASET_PATH,
        output_model_path="models/mobilenetv2_padi.pth",
        epochs=15,
        batch_size=32,
        learning_rate=0.001
    )
