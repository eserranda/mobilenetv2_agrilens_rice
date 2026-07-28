# Gunakan Node.js 20 sebagai base image
FROM node:20-alpine

# Tentukan folder kerja di dalam container
WORKDIR /app

# Salin package.json
COPY package*.json ./

# Instal dependencies dengan mengabaikan script pasca-instalasi
RUN npm ci --ignore-scripts

# Salin seluruh kode frontend
COPY . .

# Build aplikasi Next.js untuk produksi
# URL API backend dihubungkan secara default ke http://localhost:8000
ENV NEXT_PUBLIC_API_URL=http://localhost:8000 \
    PORT=3000
RUN npm run build

# Expose port 3000
EXPOSE 3000

# Jalankan server Next.js produksi saat container menyala
CMD ["npm", "run", "start"]
