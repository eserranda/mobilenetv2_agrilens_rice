"""
training/train.py
==================
Script untuk melatih model MobileNetV2 untuk mengklasifikasikan penyakit daun padi.
Mendukung 4 kelas: 'Brown Spot', 'Healthy', 'Hispa', 'Leaf Blast'.

Petunjuk penggunaan lengkap dapat dibaca di README.md dalam folder ini.
"""

import os
import time
import copy
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms, models
from pathlib import Path

# --- KELAS & LABEL YANG DIGUNAKAN ---
# Harus sesuai dengan label di models/labels.json
CLASS_LABELS = ['Bacterial blight', 'Blast', 'Brown Spot', 'Tungro']
NUM_CLASSES = len(CLASS_LABELS)

def train_model(
    data_dir: str, 
    output_model_path: str = "mobilenetv2_padi.pth", 
    epochs: int = 10, 
    batch_size: int = 32, 
    learning_rate: float = 0.001
):
    """
    Melatih model MobileNetV2 menggunakan data gambar dalam direktori data_dir.
    """
    print("==================================================")
    print("Memulai Proses Training Rice Disease Classification")
    print("==================================================")
    
    # 1. Menentukan Device (GPU jika tersedia, jika tidak menggunakan CPU)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"Device yang digunakan untuk training: {device}")
    if device.type == 'cuda':
        print(f"Nama GPU: {torch.cuda.get_device_name(0)}")

    # 2. Preprocessing & Augmentasi Gambar
    # Menggunakan ImageNet normalization standar (sama seperti saat inference)
    data_transforms = {
        'train': transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomVerticalFlip(),
            transforms.RandomRotation(15),
            transforms.ColorJitter(brightness=0.1, contrast=0.1),
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
    full_dataset = datasets.ImageFolder(root=data_dir)
    
    # Pastikan jumlah kelas sesuai
    if len(full_dataset.classes) != NUM_CLASSES:
        print(f"[PERINGATAN] Jumlah folder kelas ({len(full_dataset.classes)}) tidak sesuai dengan target ({NUM_CLASSES})!")
        print(f"Folder yang terbaca: {full_dataset.classes}")
        print(f"Target kelas kita: {CLASS_LABELS}")

    # Membagi dataset menjadi 80% Training dan 20% Validasi
    train_size = int(0.8 * len(full_dataset))
    val_size = len(full_dataset) - train_size
    
    # Gunakan random_split untuk membagi dataset
    train_subset, val_subset = random_split(
        full_dataset, 
        [train_size, val_size], 
        generator=torch.Generator().manual_seed(42)
    )

    # Terapkan transform yang berbeda untuk training dan validasi
    # Menggunakan custom dataset wrapper untuk mengaplikasikan transformasi yang dinamis
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
    dataloaders = {
        'train': DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0),
        'val': DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)
    }
    
    dataset_sizes = {
        'train': len(train_dataset),
        'val': len(val_dataset)
    }

    print(f"Total gambar training: {dataset_sizes['train']}")
    print(f"Total gambar validasi: {dataset_sizes['val']}")

    # 5. Inisialisasi Model MobileNetV2 dengan bobot pre-trained ImageNet
    print("Mendownload model dasar MobileNetV2 pre-trained...")
    try:
        # Pytorch 1.13+ syntax
        model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
    except AttributeError:
        # Pytorch lama syntax
        model = models.mobilenet_v2(pretrained=True)

    # Bekukan (freeze) feature extractor agar bobotnya tidak berubah banyak di awal training
    for param in model.parameters():
        param.requires_grad = False

    # Ganti bagian classifier/layer terakhir dengan jumlah kelas target kita (4 kelas)
    num_ftrs = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(num_ftrs, NUM_CLASSES)
    
    model = model.to(device)

    # 6. Menentukan Loss Function dan Optimizer
    criterion = nn.CrossEntropyLoss()
    
    # Hanya latih parameter di classifier (layer terakhir) agar proses cepat dan akurat
    optimizer = optim.Adam(model.classifier[1].parameters(), lr=learning_rate)

    # 7. Loop Training
    since = time.time()
    best_model_wts = copy.deepcopy(model.state_dict())
    best_acc = 0.0

    for epoch in range(epochs):
        print(f"\nEpoch {epoch+1}/{epochs}")
        print("-" * 10)

        # Setiap epoch memiliki fase training dan validasi
        for phase in ['train', 'val']:
            if phase == 'train':
                model.train()  # Set model ke mode training
            else:
                model.eval()   # Set model ke mode evaluasi

            running_loss = 0.0
            running_corrects = 0

            # Iterasi data gambar
            for inputs, labels in dataloaders[phase]:
                inputs = inputs.to(device)
                labels = labels.to(device)

                # Reset parameter gradients
                optimizer.zero_grad()

                # Forward pass
                # Lacak history jika di fase training saja
                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)

                    # Backward pass + optimize jika di fase training
                    if phase == 'train':
                        loss.backward()
                        optimizer.step()

                # Statistik akumulatif
                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)

            epoch_loss = running_loss / dataset_sizes[phase]
            epoch_acc = running_corrects.double() / dataset_sizes[phase]

            print(f"{phase.capitalize()} Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}")

            # Simpan model terbaik jika akurasi validasi meningkat
            if phase == 'val' and epoch_acc > best_acc:
                best_acc = epoch_acc
                best_model_wts = copy.deepcopy(model.state_dict())

    time_elapsed = time.time() - since
    print(f"\nTraining selesai dalam {time_elapsed // 60:.0f}m {time_elapsed % 60:.0f}s")
    print(f"Akurasi Validasi Terbaik: {best_acc:4f}")

    # 8. Memuat bobot model terbaik dan menyimpannya ke disk
    model.load_state_dict(best_model_wts)
    
    # Buat direktori output jika belum ada
    output_path = Path(output_model_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    torch.save(model.state_dict(), output_path)
    print(f"[SUCCESS] Model terlatih disimpan ke: {output_path.resolve()}")
    print("==================================================")

if __name__ == "__main__":
    # Secara default, script mencari folder data di 'training/data/'
    # Ganti path ini jika dataset Anda diletakkan di tempat lain.
    DATA_DIRECTORY = "training/data"
    
    if not os.path.exists(DATA_DIRECTORY):
        print(f"[ERROR] Folder dataset '{DATA_DIRECTORY}' tidak ditemukan!")
        print("Silakan download dataset dari Kaggle dan letakkan di dalam folder tersebut,")
        print("atau ubah variabel DATA_DIRECTORY di dalam script ini.")
    else:
        train_model(
            data_dir=DATA_DIRECTORY,
            output_model_path="models/mobilenetv2_padi.pth", # Timpa sample model dengan hasil training asli
            epochs=10,
            batch_size=32,
            learning_rate=0.001
        )
