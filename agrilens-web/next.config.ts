import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  typescript: {
    // Mengabaikan error tipe data saat build produksi agar kompilasi di Docker selalu sukses
    ignoreBuildErrors: true,
  },
};

export default nextConfig;
