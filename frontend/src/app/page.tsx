"use client";

import React, { useState, useEffect, useRef, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { 
  Upload, 
  Loader2, 
  Leaf, 
  AlertTriangle, 
  CheckCircle, 
  RefreshCw,
  Settings,
  User,
  Camera,
  Eye,
  ClipboardList,
  Wrench,
  FlaskConical,
  Ban,
  Activity,
  Cpu
} from "lucide-react";
import { 
  detectDisease, 
  getHistoryDetail, 
  DetectionResponse, 
  HistoryDetail 
} from "@/lib/api";
import { cn } from "@/lib/utils";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const SCIENTIFIC_NAMES: Record<string, string> = {
  "Bacterial blight": "Xanthomonas oryzae pv. oryzae",
  "Blast": "Magnaporthe oryzae",
  "Brown Spot": "Cochliobolus miyabeanus",
  "Tungro": "Rice Tungro Bacilliform Virus & Rice Tungro Spherical Virus",
  "Healthy": "Oryza sativa (Sehat)",
};

function DetectionContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const historyId = searchParams.get("id");

  // --- States ---
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<DetectionResponse | HistoryDetail | null>(null);
  const [activeTab, setActiveTab] = useState<"result" | "analysis">("result");
  const [dragActive, setDragActive] = useState<boolean>(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // --- Fetch detailed log if searchParam ID is set ---
  useEffect(() => {
    if (historyId) {
      loadHistoryDetail(historyId);
    } else {
      // Clear screen state if navigating back to root
      setSelectedFile(null);
      setPreviewUrl(null);
      setResult(null);
      setError(null);
    }
  }, [historyId]);

  const loadHistoryDetail = async (id: string) => {
    setIsLoading(true);
    setError(null);
    setSelectedFile(null);
    setPreviewUrl(null);
    try {
      const detail = await getHistoryDetail(id);
      setResult(detail);
    } catch (err: any) {
      setError("Gagal memuat detail riwayat diagnosis.");
    } finally {
      setIsLoading(false);
    }
  };

  // --- File input trigger ---
  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      processFile(file);
    }
  };

  const processFile = (file: File) => {
    setSelectedFile(file);
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    setResult(null);
    setError(null);
    // Clear search param
    router.replace("/");
  };

  // --- Drag & Drop ---
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  // --- Submit detection request ---
  const handleSubmit = async () => {
    if (!selectedFile) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await detectDisease(selectedFile);
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Gagal memproses gambar. Pastikan format dan koneksi sesuai.");
    } finally {
      setIsLoading(false);
    }
  };

  const resetAll = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setResult(null);
    setError(null);
    router.replace("/");
  };

  // --- Helpers for formatting and display ---
  const getImageSource = () => {
    if (previewUrl) return previewUrl;
    if (result && "image_path" in result && result.image_path) {
      return `${API_BASE_URL}${result.image_path}`;
    }
    return null;
  };

  const formatBulletPoints = (text: string | null): string[] => {
    if (!text) return [];
    return text
      .split(/[.\n]/)
      .map(sentence => sentence.trim())
      .filter(sentence => sentence.length > 5);
  };

  // Cycle through appropriate recommendation icons
  const getRecommendationIcon = (index: number) => {
    if (index % 3 === 0) return <Wrench className="h-5 w-5 text-emerald-400" />;
    if (index % 3 === 1) return <FlaskConical className="h-5 w-5 text-emerald-400" />;
    return <Ban className="h-5 w-5 text-emerald-400" />;
  };

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* ============================================== HEADER SECTION */}
      <header className="h-16 border-b border-slate-900 px-6 flex items-center justify-between shrink-0 bg-slate-950/50 z-10">
        <div className="flex items-center gap-6">
          <button
            onClick={() => setActiveTab("result")}
            className={cn(
              "h-16 text-sm font-bold tracking-wide relative flex items-center transition",
              activeTab === "result" ? "text-emerald-400" : "text-slate-400 hover:text-slate-200"
            )}
          >
            Detection Result
            {activeTab === "result" && (
              <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-emerald-400" />
            )}
          </button>
          <button
            onClick={() => setActiveTab("analysis")}
            className={cn(
              "h-16 text-sm font-bold tracking-wide relative flex items-center transition",
              activeTab === "analysis" ? "text-emerald-400" : "text-slate-400 hover:text-slate-200"
            )}
          >
            Current Analysis
            {activeTab === "analysis" && (
              <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-emerald-400" />
            )}
          </button>
        </div>

        <div className="flex items-center gap-4">
          <button 
            onClick={resetAll} 
            className="text-slate-400 hover:text-white transition p-1.5 hover:bg-slate-900 rounded-lg"
            title="Reset Scan"
          >
            <RefreshCw className="h-5 w-5" />
          </button>
          <button className="text-slate-400 hover:text-white transition p-1.5 hover:bg-slate-900 rounded-lg">
            <Settings className="h-5 w-5" />
          </button>
          <div className="h-8 w-8 rounded-full bg-slate-800 border border-slate-700 overflow-hidden flex items-center justify-center">
            <User className="h-4.5 w-4.5 text-slate-400" />
          </div>
        </div>
      </header>

      {/* ============================================== CONTENT CONTAINER */}
      <div className="flex-1 overflow-y-auto p-4 md:p-6 bg-gradient-to-br from-slate-900 via-slate-950 to-slate-900">
        <div className="max-w-6xl mx-auto space-y-6">

          {/* Error Banner */}
          {error && (
            <div className="p-4 bg-rose-500/15 border border-rose-500/30 rounded-2xl flex items-start gap-3">
              <AlertTriangle className="h-5 w-5 text-rose-400 shrink-0 mt-0.5" />
              <div>
                <h4 className="font-bold text-rose-400 text-sm">Terjadi Masalah</h4>
                <p className="text-xs text-rose-300/80 mt-0.5">{error}</p>
              </div>
            </div>
          )}

          {/* Hidden native input */}
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept="image/*"
            className="hidden"
          />

          {isLoading && !result && (
            /* Analysis Loading Screen */
            <div className="border border-slate-850/80 bg-slate-950/40 rounded-3xl p-12 text-center flex flex-col items-center justify-center min-h-[400px]">
              <Loader2 className="h-12 w-12 text-emerald-400 animate-spin mb-4" />
              <h3 className="font-bold text-slate-200 text-lg">Menganalisis Kesehatan Daun Padi...</h3>
              <p className="text-xs text-slate-500 max-w-sm mt-1.5 leading-relaxed">
                Sistem sedang mengidentifikasi karakteristik visual pada daun menggunakan MobileNetV2 dan merumuskan diagnosis menggunakan AI Pathologist.
              </p>
            </div>
          )}

          {!isLoading && !result && (
            /* Upload Screen (Desktop Drag-drop / Mobile Camera button) */
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              <div className="lg:col-span-12">
                {/* Desktop Upload Area */}
                <div 
                  onDragEnter={handleDrag}
                  onDragOver={handleDrag}
                  onDragLeave={handleDrag}
                  onDrop={handleDrop}
                  onClick={triggerFileInput}
                  className={cn(
                    "hidden md:flex border-2 border-dashed rounded-3xl p-12 transition duration-300 flex-col items-center justify-center min-h-[350px] relative overflow-hidden bg-slate-950/20 border-slate-800 hover:border-slate-700 cursor-pointer"
                  )}
                >
                  <div className="h-16 w-16 rounded-2xl bg-slate-850 border border-slate-800 flex items-center justify-center text-emerald-400 mb-4 hover:scale-105 transition duration-300">
                    <Upload className="h-6 w-6" />
                  </div>
                  <h3 className="font-bold text-slate-200 text-lg">Unggah Gambar Daun Padi</h3>
                  <p className="text-xs text-slate-550 max-w-xs mt-1 text-center">
                    Seret & lepas foto di sini, atau klik untuk memilih file dari komputer Anda (JPG, PNG, WebP)
                  </p>
                </div>

                {/* Mobile Upload Area */}
                <div className="block md:hidden border border-slate-800 rounded-3xl p-8 bg-slate-950/20 backdrop-blur-md text-center">
                  <div className="flex flex-col items-center justify-center">
                    <div className="h-14 w-14 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 mb-4">
                      <Camera className="h-6 w-6" />
                    </div>
                    <h3 className="font-bold text-slate-200 text-base">Ambil Foto / Pilih File</h3>
                    <p className="text-xs text-slate-500 max-w-xs mt-2 mb-6 leading-relaxed">
                      Ambil foto daun padi secara langsung menggunakan kamera HP Anda, atau pilih file gambar yang sudah ada.
                    </p>
                    <button
                      onClick={triggerFileInput}
                      className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 active:bg-emerald-700 rounded-2xl font-semibold flex items-center justify-center gap-2 transition duration-200 text-sm text-white"
                    >
                      <Camera className="h-4.5 w-4.5" />
                      Ambil Foto / Pilih File
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {result && !isLoading && (
            /* ============================================== RESULT VIEW (AgriLens Pro layout) */
            <div className="space-y-6">
              
              {/* TOP ROW: Leaf Image & Disease Card */}
              <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-start">
                
                {/* 1. Image Preview Panel */}
                <div className="md:col-span-5 space-y-4">
                  <div className="border border-slate-800/80 bg-slate-950/40 rounded-3xl p-4 relative backdrop-blur-md">
                    <div className="w-full aspect-square relative rounded-2xl overflow-hidden border border-slate-900 bg-slate-950">
                      <img
                        src={getImageSource()!}
                        alt={result.disease}
                        className="h-full w-full object-contain"
                      />
                      
                      {/* AI Verified badge overlay */}
                      <span className="absolute top-3 left-3 bg-emerald-500/80 backdrop-blur-md text-white text-[10px] font-bold tracking-wider px-2.5 py-1 rounded-full uppercase border border-emerald-400/25">
                        AI Verified
                      </span>
                    </div>

                    {/* Scan actions below image */}
                    <div className="grid grid-cols-2 gap-3 mt-4">
                      <button 
                        onClick={triggerFileInput}
                        className="py-2.5 bg-emerald-800 hover:bg-emerald-700 active:bg-emerald-900 text-white rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 transition"
                      >
                        <Camera className="h-4 w-4" />
                        Scan New
                      </button>
                      <button 
                        onClick={triggerFileInput}
                        className="py-2.5 bg-slate-900 hover:bg-slate-855 text-emerald-400 hover:text-emerald-300 border border-slate-800 hover:border-slate-700 rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 transition"
                      >
                        <Upload className="h-4 w-4" />
                        Upload File
                      </button>
                    </div>
                  </div>
                </div>

                {/* 2. Disease details card */}
                <div className="md:col-span-7 space-y-6">
                  
                  {/* Title and Matching bar */}
                  <div className="border border-slate-800/80 bg-slate-950/40 rounded-3xl p-6 backdrop-blur-md relative">
                    <div className="flex flex-wrap items-start justify-between gap-4">
                      <div>
                        <h2 className="text-2xl font-extrabold text-white">{result.disease}</h2>
                        <p className="text-xs text-slate-400 italic mt-1.5 font-medium">
                          {SCIENTIFIC_NAMES[result.disease] || "Oryza sativa pathogens"}
                        </p>
                      </div>

                      {/* Action / Healthy status pill */}
                      {result.disease === "Healthy" ? (
                        <div className="px-3 py-1 text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-full flex items-center gap-1">
                          <CheckCircle className="h-3.5 w-3.5" />
                          SEHAT / AMAN
                        </div>
                      ) : (
                        <div className="px-3 py-1 text-[10px] font-bold bg-rose-500/10 text-rose-500 border border-rose-500/20 rounded-full flex items-center gap-1">
                          <AlertTriangle className="h-3.5 w-3.5" />
                          ACTION REQUIRED
                        </div>
                      )}
                    </div>

                    {/* Progress Gauge */}
                    <div className="mt-8 space-y-2">
                      <div className="flex items-center justify-between text-xs font-semibold">
                        <span className="text-slate-400">MobileNetV2 Match Confidence</span>
                        <span className="text-emerald-400">{Math.round(result.confidence * 100)}%</span>
                      </div>
                      <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-gradient-to-r from-emerald-500 to-teal-400 transition-all duration-1000 ease-out"
                          style={{ width: `${result.confidence * 100}%` }}
                        />
                      </div>
                      <p className="text-[10px] text-slate-500 text-right">
                        Inference Time: {result.inference_time_ms.toFixed(1)} ms
                      </p>
                    </div>
                  </div>

                  {/* Two columns details: Symptoms observed & Recommended actions */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                    
                    {/* Symptoms observed Card */}
                    <div className="border border-slate-800/80 bg-slate-950/40 rounded-3xl p-5 backdrop-blur-md">
                      <div className="flex items-center gap-2 mb-4 border-b border-slate-800/60 pb-3">
                        <Eye className="h-5 w-5 text-emerald-400" />
                        <h4 className="font-bold text-sm text-slate-200">Symptoms Observed</h4>
                      </div>
                      
                      {result.explanation ? (
                        <ul className="space-y-3">
                          {formatBulletPoints(result.explanation).map((pt, i) => (
                            <li key={i} className="text-xs text-slate-300 leading-relaxed flex items-start gap-2">
                              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 mt-1.5 shrink-0" />
                              <span>{pt}</span>
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="text-xs text-slate-500 italic">Tidak ada deskripsi gejala teramati.</p>
                      )}
                    </div>

                    {/* Recommended actions Card */}
                    <div className="border border-slate-800/80 bg-slate-950/40 rounded-3xl p-5 backdrop-blur-md">
                      <div className="flex items-center gap-2 mb-4 border-b border-slate-800/60 pb-3">
                        <ClipboardList className="h-5 w-5 text-emerald-400" />
                        <h4 className="font-bold text-sm text-slate-200">Recommended Actions</h4>
                      </div>

                      {result.recommendation ? (
                        <ul className="space-y-3">
                          {formatBulletPoints(result.recommendation).map((pt, i) => (
                            <li key={i} className="text-xs text-slate-350 leading-relaxed flex items-start gap-3 bg-slate-900/30 p-2.5 rounded-xl border border-slate-800/30">
                              <div className="h-7 w-7 rounded-lg bg-emerald-500/10 flex items-center justify-center shrink-0 mt-0.5">
                                {getRecommendationIcon(i)}
                              </div>
                              <span>{pt}</span>
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="text-xs text-slate-500 italic">Tidak ada rekomendasi penanganan.</p>
                      )}
                    </div>

                  </div>

                </div>

              </div>

              {/* BOTTOM ROW: Timeline AI Diagnostic Reasoning (CoT) */}
              {result.thinking && (
                <div className="border border-slate-800/85 bg-slate-950/40 rounded-3xl p-6 backdrop-blur-md space-y-6">
                  
                  {/* Section Title */}
                  <div className="flex items-center gap-2 border-b border-slate-800/80 pb-4">
                    <Activity className="h-5 w-5 text-emerald-400" />
                    <h3 className="font-bold text-base text-white">AI Diagnostic Reasoning</h3>
                  </div>

                  {/* Custom Timeline steps */}
                  <div className="space-y-6 relative before:absolute before:left-3 before:top-2 before:bottom-2 before:w-[1px] before:bg-slate-800">
                    
                    {/* Step 1: Pre-processing */}
                    <div className="flex gap-4 relative">
                      <div className="h-6.5 w-6.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center z-10 shrink-0 text-emerald-400">
                        <CheckCircle className="h-4.5 w-4.5 text-emerald-400" />
                      </div>
                      <div className="space-y-1">
                        <h5 className="font-bold text-xs text-slate-200 tracking-wide">Image Pre-processing Complete</h5>
                        <p className="text-xs text-slate-450 leading-relaxed max-w-2xl">
                          Normalisasi dan scaling citra diaplikasikan. Matriks input [{("metadata" in result && result.metadata && result.metadata.input_size) ? result.metadata.input_size.join("x") : "224x224"}] disiapkan untuk pemetaan fitur MobileNetV2.
                        </p>
                      </div>
                    </div>

                    {/* Step 2: Feature Extraction */}
                    <div className="flex gap-4 relative">
                      <div className="h-6.5 w-6.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center z-10 shrink-0 text-emerald-400">
                        <CheckCircle className="h-4.5 w-4.5 text-emerald-400" />
                      </div>
                      <div className="space-y-1">
                        <h5 className="font-bold text-xs text-slate-200 tracking-wide">Feature Extraction</h5>
                        <p className="text-xs text-slate-450 leading-relaxed max-w-2xl">
                          Model ekstraktor MobileNetV2 mengidentifikasi bentuk, gradien warna klorosis, dan kluster lesi nekrotik pada permukaan daun padi.
                        </p>
                      </div>
                    </div>

                    {/* Step 3: Multimodal Cross-Reference */}
                    <div className="flex gap-4 relative">
                      <div className="h-6.5 w-6.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center z-10 shrink-0 text-emerald-400">
                        <CheckCircle className="h-4.5 w-4.5 text-emerald-400" />
                      </div>
                      <div className="space-y-1">
                        <h5 className="font-bold text-xs text-slate-200 tracking-wide">Multimodal Cross-Reference</h5>
                        <p className="text-xs text-slate-450 leading-relaxed max-w-2xl">
                          Mengintegrasikan bobot probabilitas model klasifikasi visi dengan penalaran logika AI Pathologist menggunakan basis pengetahuan diagnosis padi.
                        </p>
                      </div>
                    </div>

                    {/* Step 4: OpenAI CoT Reasoning */}
                    <div className="flex gap-4 relative">
                      <div className="h-6.5 w-6.5 rounded-full bg-emerald-500 border border-emerald-400 flex items-center justify-center z-10 shrink-0 text-slate-950">
                        <Cpu className="h-3.5 w-3.5 text-slate-950 font-bold" />
                      </div>
                      <div className="space-y-2 flex-1">
                        <h5 className="font-bold text-xs text-emerald-400 tracking-wide">Diagnostic Finalization & Chain-of-Thought</h5>
                        
                        <div className="bg-slate-950/60 p-4 rounded-2xl border border-slate-800/80 max-w-4xl">
                          <p className="text-xs text-slate-350 leading-relaxed font-mono whitespace-pre-line select-text">
                            {result.thinking}
                          </p>
                        </div>
                      </div>
                    </div>

                  </div>
                </div>
              )}

            </div>
          )}

        </div>
      </div>
    </div>
  );
}

export default function Dashboard() {
  return (
    <Suspense fallback={
      <div className="flex-1 flex items-center justify-center bg-slate-900">
        <Loader2 className="h-10 w-10 text-emerald-500 animate-spin" />
      </div>
    }>
      <DetectionContent />
    </Suspense>
  );
}
