# Gunakan image Python 3.12 slim sebagai base image
FROM python:3.12-slim

# Atur environment variables untuk Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Set working directory di dalam container
WORKDIR /app


# Salin file requirements.txt terlebih dahulu untuk memanfaatkan Docker cache
COPY requirements.txt .

# Upgrade pip dan instal dependencies Python
# Catatan: Kita mengunduh PyTorch versi CPU agar ukuran image Docker tetap kecil (tidak mengunduh CUDA yang berukuran gigabytes)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt

# Salin source code aplikasi dan model
COPY app/ ./app/
COPY models/ ./models/

# Expose port yang digunakan aplikasi
EXPOSE 8000

# Jalankan server uvicorn saat container dimulai
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
