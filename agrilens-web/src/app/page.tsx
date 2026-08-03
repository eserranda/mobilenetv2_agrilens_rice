"use client";

import React from "react";
import Link from "next/link";
import {
  Leaf,
  History,
  Cpu,
  Database,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  Sparkles,
  BookOpen,
  HelpCircle
} from "lucide-react";

export default function LandingPage() {
  const features = [
    {
      icon: Cpu,
      title: "Klasifikasi Visi Cepat",
      description: "Model deep learning MobileNetV2 yang dioptimalkan mengekstrak pola lesi dan warna daun secara instan."
    },
    {
      icon: Sparkles,
      title: "AI Pathologist (LLM)",
      description: "Penalaran Chain-of-Thought (CoT) merumuskan diagnosis gejala dan rekomendasi penanganan daun secara mendalam."
    },
    {
      icon: ShieldCheck,
      title: "Vision Guardrail",
      description: "Validasi berbasis OpenAI Vision menyaring subjek non-daun padi (hewan, wajah) secara otomatis demi keaslian data."
    },
    {
      icon: Database,
      title: "Riwayat Terintegrasi",
      description: "Hasil diagnosa dicatat secara aman dalam database SQLite lokal untuk pemantauan kesehatan berkala."
    }
  ];

  const steps = [
    {
      step: "01",
      title: "Ambil & Unggah Foto",
      description: "Foto daun padi yang dicurigai sakit menggunakan kamera atau pilih dari galeri perangkat Anda."
    },
    {
      step: "02",
      title: "Analisis Visi & AI",
      description: "MobileNetV2 mengidentifikasi jenis penyakit sementara AI Pathologist menyusun penjelasan ilmiah."
    },
    {
      step: "03",
      title: "Tindakan Presisi",
      description: "Dapatkan saran penanganan praktis dan rekomendasi pupuk/pestisida yang sesuai secara langsung."
    }
  ];

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 bg-gradient-to-b from-emerald-100/60 via-white to-slate-100 text-slate-800">

      {/* 1. NAVIGATION HEADER */}
      <header className="sticky top-0 z-50 bg-white/85 backdrop-blur-md border-b border-slate-100 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="h-9 w-9 rounded-xl bg-emerald-600/10 border border-emerald-500/20 flex items-center justify-center text-emerald-600">
              <Leaf className="h-5 w-5 fill-current" />
            </div>
            <div>
              <h1 className="font-extrabold text-lg leading-none tracking-tight text-slate-900">AgriLens Pro</h1>
              <p className="text-[10px] text-emerald-600 font-bold tracking-wider uppercase mt-0.5">Precision Diagnostics</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <Link
              href="/detection"
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 active:bg-emerald-700 text-white rounded-xl text-xs font-bold shadow-md shadow-emerald-600/10 transition duration-200"
            >
              Coba Sekarang
            </Link>
          </div>
        </div>
      </header>

      {/* 2. HERO SECTION */}
      <section className="flex-1 max-w-6xl mx-auto px-6 py-16 md:py-24 grid grid-cols-1 md:grid-cols-12 gap-12 items-center">

        {/* Left Column: Headline */}
        <div className="md:col-span-7 space-y-6 text-left">
          <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-500/10 text-emerald-700 border border-emerald-500/10 text-[10px] font-bold tracking-wide uppercase">
            <Sparkles className="h-3.5 w-3.5" />
            Kecerdasan Buatan Agroteknologi
          </div>

          <h1 className="text-4xl md:text-5xl font-black text-slate-900 leading-tight tracking-tight">
            Deteksi Dini Penyakit <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-600 to-teal-500">
              Daun Padi Berbasis AI
            </span>
          </h1>

          <p className="text-sm md:text-base text-slate-600 leading-relaxed max-w-xl">
            Solusi praktis berbasis visi komputer MobileNetV2 dan model bahasa untuk mendiagnosa patologi tanaman padi. Unggah foto daun padi, dapatkan diagnosa penyakit serta rekomendasi penanganan presisi secara instan.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-wrap gap-4 pt-2">
            <Link
              href="/detection"
              className="px-6 py-3.5 bg-emerald-600 hover:bg-emerald-500 active:bg-emerald-700 text-white rounded-2xl text-sm font-bold flex items-center gap-2 shadow-lg shadow-emerald-600/20 transition-all duration-300 transform hover:-translate-y-0.5"
            >
              Mulai Analisis Daun
              <ArrowRight className="h-4.5 w-4.5" />
            </Link>
          </div>

          {/* Quick Info Grid */}
          <div className="grid grid-cols-3 gap-6 pt-8 border-t border-slate-100 max-w-lg">
            <div>
              <h4 className="text-xl md:text-2xl font-black text-slate-900 leading-none">4 Kelas</h4>
              <p className="text-[10px] text-slate-500 font-medium uppercase tracking-wider mt-1">Target Penyakit & Sehat</p>
            </div>
            <div>
              <h4 className="text-xl md:text-2xl font-black text-slate-900 leading-none">&lt; 200 ms</h4>
              <p className="text-[10px] text-slate-500 font-medium uppercase tracking-wider mt-1">Inference Time lokal</p>
            </div>
            <div>
              <h4 className="text-xl md:text-2xl font-black text-slate-900 leading-none">100%</h4>
              <p className="text-[10px] text-slate-500 font-medium uppercase tracking-wider mt-1">AI-Powered Solutions</p>
            </div>
          </div>
        </div>

        {/* Right Column: Visual Mockup card */}
        <div className="md:col-span-5 relative">

          {/* Background Decorative blob */}
          <div className="absolute inset-0 bg-gradient-to-tr from-emerald-400/10 to-teal-400/20 rounded-full blur-3xl -z-10 transform scale-95" />

          {/* Mockup Card */}
          <div className="bg-white rounded-3xl border border-slate-100 p-4 shadow-2xl shadow-slate-200/80 max-w-sm mx-auto space-y-3">
            <div className="flex items-center justify-between border-b border-slate-50 pb-1">
              <span className="text-[10px] font-extrabold text-slate-400 tracking-wider uppercase">Preview Analisis</span>
              <span className="px-2 py-0.5 bg-emerald-500/10 text-emerald-600 rounded-full text-[9px] font-bold">Model Ready</span>
            </div>

            <div className="aspect-[4/4] rounded-2xl bg-slate-100 border border-slate-100 relative overflow-hidden group">
              <img
                src="/img/rice2.jpg"
                alt="Daun Padi Sehat"
                className="h-full w-full object-cover brightness-[0.9] transition duration-700 group-hover:scale-105"
              />

              {/* Floating Match Card */}
              <div className="absolute bottom-3 left-3 right-3 bg-white/95 backdrop-blur-sm border border-slate-100 p-3 rounded-xl shadow-lg flex items-center justify-between z-10">
                <div className="flex items-center gap-2">
                  <div className="h-7 w-7 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-600">
                    <CheckCircle2 className="h-4.5 w-4.5" />
                  </div>
                  <div>
                    <h5 className="text-[10px] font-extrabold text-slate-800 leading-none">Healthy</h5>
                    <p className="text-[8px] text-slate-400 mt-0.5">Klasifikasi Sukses</p>
                  </div>
                </div>
                <span className="text-[10px] font-black text-emerald-600">97% Match</span>
              </div>
            </div>

            {/* Quick action buttons mockup */}
            <div className="space-y-2">
              <div className="h-2 w-full bg-slate-100 rounded-full" />
              <div className="h-2 w-5/6 bg-slate-100 rounded-full" />
              <div className="h-2 w-2/3 bg-slate-100 rounded-full" />
            </div>
          </div>
        </div>

      </section>

      {/* 3. CORE FEATURES SECTION */}
      <section className="bg-slate-50 border-y border-slate-100 py-16 md:py-24">
        <div className="max-w-6xl mx-auto px-6 text-center space-y-12">

          <div className="space-y-3 max-w-xl mx-auto">
            <h2 className="text-xs font-extrabold text-emerald-600 tracking-widest uppercase">Teknologi Mutakhir</h2>
            <h3 className="text-2xl md:text-3xl font-black text-slate-900 tracking-tight">Fitur Unggulan AgriLens Pro</h3>
            <p className="text-xs md:text-sm text-slate-500 leading-relaxed">
              Kami menggabungkan klasifikasi gambar yang cepat berbasis komputasi lokal dengan kecerdasan kognitif model bahasa besar untuk hasil diagnosa maksimal.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feat, i) => {
              const Icon = feat.icon;
              return (
                <div
                  key={i}
                  className="bg-white border border-slate-100 rounded-2xl p-6 text-left shadow-sm hover:shadow-md transition-all duration-300 hover:scale-102"
                >
                  <div className="h-10 w-10 rounded-xl bg-emerald-500/10 flex items-center justify-center text-emerald-600 mb-4.5">
                    <Icon className="h-5 w-5" />
                  </div>
                  <h4 className="font-bold text-sm text-slate-900 mb-2">{feat.title}</h4>
                  <p className="text-xs text-slate-500 leading-relaxed">{feat.description}</p>
                </div>
              );
            })}
          </div>

        </div>
      </section>

      {/* 4. WORKFLOW SECTION */}
      <section className="py-16 md:py-24">
        <div className="max-w-6xl mx-auto px-6 text-center space-y-12">

          <div className="space-y-3 max-w-xl mx-auto">
            <h2 className="text-xs font-extrabold text-emerald-600 tracking-widest uppercase">Alur Kerja Sistem</h2>
            <h3 className="text-2xl md:text-3xl font-black text-slate-900 tracking-tight">Hanya 3 Langkah Mudah</h3>
            <p className="text-xs md:text-sm text-slate-500 leading-relaxed">
              Deteksi dilakukan secara mandiri dari browser Anda, terintegrasi langsung dengan API server.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
            {steps.map((step, i) => (
              <div key={i} className="space-y-4 text-center px-4 relative">
                <div className="h-16 w-16 rounded-full bg-white border-2 border-emerald-500/20 flex items-center justify-center mx-auto text-emerald-600 font-black text-lg shadow-md shadow-emerald-500/5">
                  {step.step}
                </div>
                <h4 className="font-bold text-sm text-slate-900">{step.title}</h4>
                <p className="text-xs text-slate-500 leading-relaxed max-w-xs mx-auto">{step.description}</p>
              </div>
            ))}
          </div>

        </div>
      </section>

      {/* 5. bottom cta banner */}
      <section className="max-w-6xl w-full mx-auto px-6 pb-16">
        <div className="bg-gradient-to-r from-emerald-600 to-teal-500 rounded-3xl p-8 md:p-12 text-center text-white space-y-6 shadow-xl shadow-emerald-600/10 relative overflow-hidden">

          {/* Decorative shapes */}
          <div className="absolute -top-10 -left-10 h-32 w-32 rounded-full bg-white/5 blur-2xl" />
          <div className="absolute -bottom-10 -right-10 h-32 w-32 rounded-full bg-white/5 blur-2xl" />

          <h2 className="text-2xl md:text-3xl font-black tracking-tight leading-tight">
            Rawat Tanaman Padi Anda Sekarang
          </h2>
          <p className="text-xs md:text-sm text-emerald-50/90 leading-relaxed max-w-xl mx-auto">
            Dapatkan diagnosa visual penyakit seperti Blas, Hawar Daun Bakteri (Bacterial Blight), Bercak Cokelat (Brown Spot), atau pastikan kondisi tanaman padi Anda sehat secara instan.
          </p>

          <div className="pt-4">
            <Link
              href="/detection"
              className="inline-flex items-center gap-2 px-6 py-3.5 bg-white text-emerald-700 hover:bg-slate-50 rounded-2xl text-sm font-extrabold shadow-lg transition-all duration-200 transform hover:scale-103"
            >
              Mulai Uji Coba
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* 6. FOOTER */}
      <footer className="mt-auto bg-slate-900 text-slate-400 py-12 px-6 border-t border-slate-800 text-xs">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2">
            <div className="h-6 w-6 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-400">
              <Leaf className="h-3.5 w-3.5 fill-current" />
            </div>
            <span className="font-extrabold text-sm text-white">AgriLens Pro</span>
          </div>

          <p className="text-center sm:text-right text-slate-500">
            &copy; 2026 AgriLens Pro. Dibuat untuk Keperluan Penelitian Skripsi Universitas Kristen Indonesia Paulus Makassar</p>
        </div>
      </footer>

    </div>
  );
}
