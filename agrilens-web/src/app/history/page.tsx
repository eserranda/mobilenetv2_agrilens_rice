"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  History,
  Trash2,
  Loader2,
  ChevronRight,
  Download,
  Search,
  Calendar,
  SlidersHorizontal,
  CheckCircle,
  Plus,
  Camera,
  AlertTriangle,
  User
} from "lucide-react";
import {
  getHistory,
  deleteHistory,
  HistoryItem
} from "@/lib/api";
import { cn } from "@/lib/utils";
import Header from "@/components/Header";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function HistoryPage() {
  // --- States ---
  const [historyItems, setHistoryItems] = useState<HistoryItem[]>([]);
  const [totalItems, setTotalItems] = useState<number>(0);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [dateFilter, setDateFilter] = useState<string>("");
  const [activeCategory, setActiveCategory] = useState<string>("Semua");

  const categories = ["Semua", "Bacterial_Blight", "Blast", "Brown_Spot", "Healthy"];

  const loadHistory = async (page: number = 1) => {
    setIsLoading(true);
    setError(null);
    try {
      // Fetch a larger page size for grid layout (e.g. 12 items)
      const response = await getHistory(page, 12);
      setHistoryItems(response.items);
      setTotalItems(response.total);
      setCurrentPage(page);
    } catch (err) {
      setError("Gagal memuat riwayat diagnosis. Pastikan backend sudah aktif.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadHistory(1);
  }, []);

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!confirm("Apakah Anda yakin ingin menghapus log riwayat ini beserta gambarnya?")) {
      return;
    }
    try {
      await deleteHistory(id);
      loadHistory(currentPage);
    } catch (err) {
      alert("Gagal menghapus riwayat.");
    }
  };

  // --- Export to CSV ---
  const handleExportCSV = () => {
    if (historyItems.length === 0) {
      alert("Tidak ada data untuk diexport!");
      return;
    }
    const headers = ["ID", "Diagnosis", "Confidence", "Inference Time (ms)", "Severity", "Created At"];
    const rows = historyItems.map(item => [
      item.id,
      item.disease,
      `${Math.round(item.confidence * 100)}%`,
      item.inference_time_ms.toFixed(1),
      item.severity || "N/A",
      new Date(item.created_at).toISOString()
    ]);

    const csvContent = "data:text/csv;charset=utf-8,"
      + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "riwayat_deteksi_agrilens.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // --- Client-side filtering logic ---
  const filteredItems = historyItems.filter((item) => {
    // 1. Search Query
    const query = searchQuery.toLowerCase();
    const matchesSearch =
      item.disease.toLowerCase().includes(query) ||
      (item.severity && item.severity.toLowerCase().includes(query));

    // 2. Date Filter
    const matchesDate = !dateFilter || item.created_at.startsWith(dateFilter);

    // 3. Category Pill
    const matchesCategory =
      activeCategory === "Semua" ||
      item.disease.toLowerCase() === activeCategory.toLowerCase();

    return matchesSearch && matchesDate && matchesCategory;
  });

  const getBadgeStyles = (disease: string) => {
    const d = disease.toLowerCase().replace(/_/g, " ");
    if (d === "healthy") return "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
    if (d === "bacterial blight") return "bg-rose-500/10 text-rose-400 border-rose-500/20";
    return "bg-amber-500/10 text-amber-400 border-amber-500/20";
  };

  const getPillLabel = (disease: string) => {
    const d = disease.replace(/_/g, " ");
    if (d.toLowerCase() === "healthy") return "Sehat";
    return d;
  };

  // Pagination calculation
  const totalPages = Math.ceil(totalItems / 12);
  const paginationRange = Array.from({ length: Math.min(5, totalPages) }, (_, i) => i + 1);

  return (
    <div className="flex-1 flex flex-col overflow-hidden h-full min-h-0">
      {/* ============================================== TOP BAR / FILTER ACTIONS */}
      <Header />

      {/* ============================================== SCROLLABLE LIST AREA */}
      <div className="flex-1 overflow-y-auto p-4 md:p-6 bg-gradient-to-br from-slate-900 via-slate-950 to-slate-900">
        <div className="max-w-6xl mx-auto space-y-6">

          {/* Title and Export button */}
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h2 className="text-2xl font-extrabold text-white tracking-wide">Riwayat Deteksi</h2>
              <p className="text-xs text-slate-400 mt-1">Review and manage your previous plant diagnostic results.</p>
            </div>

            <button
              onClick={handleExportCSV}
              className="px-4 py-2.5 bg-slate-900 hover:bg-slate-800 border border-slate-800 text-xs font-bold rounded-xl flex items-center gap-2 transition"
            >
              <Download className="h-4 w-4" />
              Export Data
            </button>
          </div>

          {/* Filter Bar Controls */}
          <div className="bg-slate-950/40 p-4 rounded-3xl border border-slate-800/60 space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-12 gap-4">

              {/* Search Field */}
              <div className="lg:col-span-8 relative">
                <Search className="absolute left-3 top-3 h-4.5 w-4.5 text-slate-500" />
                <input
                  type="text"
                  placeholder="Search by disease, date (e.g. 2026), or status..."
                  className="w-full pl-10 pr-4 py-2.5 text-xs bg-slate-900/60 border border-slate-800 rounded-xl focus:border-emerald-500 focus:outline-none transition text-slate-200"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>

              {/* Date selector */}
              <div className="lg:col-span-4 relative flex items-center gap-2">
                <span className="text-xs text-slate-400 shrink-0">Filter by Date:</span>
                <div className="relative flex-1">
                  <Calendar className="absolute left-3 top-3 h-4.5 w-4.5 text-slate-500 pointer-events-none" />
                  <input
                    type="date"
                    className="w-full pl-10 pr-3 py-2.5 text-xs bg-slate-900/60 border border-slate-800 rounded-xl focus:border-emerald-500 focus:outline-none transition text-slate-200"
                    value={dateFilter}
                    onChange={(e) => setDateFilter(e.target.value)}
                  />
                </div>
              </div>

            </div>

            {/* Category pills filter row */}
            <div className="flex flex-wrap gap-2 pt-2 border-t border-slate-800/40">
              {categories.map((cat) => (
                <button
                  key={cat}
                  onClick={() => setActiveCategory(cat)}
                  className={cn(
                    "px-4 py-1.5 rounded-full text-xs font-semibold border transition duration-200",
                    activeCategory === cat
                      ? "bg-emerald-600 border-emerald-500 text-white shadow-md shadow-emerald-600/10"
                      : "bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200"
                  )}
                >
                  {getPillLabel(cat)}
                </button>
              ))}
            </div>
          </div>

          {/* Error display */}
          {error && (
            <div className="p-4 bg-rose-500/15 border border-rose-500/30 rounded-2xl text-center text-rose-400 text-sm">
              {error}
            </div>
          )}

          {/* History Grid Loader */}
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-20">
              <Loader2 className="h-10 w-10 text-emerald-400 animate-spin mb-4" />
              <p className="text-xs text-slate-500">Memuat log riwayat...</p>
            </div>
          ) : filteredItems.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-20 border border-dashed border-slate-800 rounded-3xl bg-slate-950/10">
              <History className="h-12 w-12 text-slate-700 mb-2" />
              <p className="text-sm font-semibold text-slate-400">Tidak ada riwayat ditemukan</p>
              <p className="text-xs text-slate-600 mt-1">Coba sesuaikan kata kunci pencarian atau pill filter Anda.</p>
            </div>
          ) : (
            /* Card Grid */
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredItems.map((item) => (
                <div
                  key={item.id}
                  className="group bg-slate-950/40 border border-slate-800/80 rounded-3xl overflow-hidden hover:border-slate-700 transition duration-300 flex flex-col relative"
                >
                  {/* Image container */}
                  <div className="w-full aspect-[4/3] bg-slate-950 relative overflow-hidden">
                    <img
                      src={`${API_BASE_URL}${item.image_path}`}
                      alt={item.disease}
                      className="w-full h-full object-cover group-hover:scale-105 transition duration-500"
                      loading="lazy"
                    />

                    {/* Floating label badge */}
                    <span className={cn(
                      "absolute top-3 left-3 text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-full border backdrop-blur-md",
                      getBadgeStyles(item.disease)
                    )}>
                      {getPillLabel(item.disease)}
                    </span>

                    {/* Delete action overlay */}
                    <button
                      onClick={(e) => handleDelete(item.id, e)}
                      className="absolute top-3 right-3 p-1.5 bg-slate-950/80 hover:bg-rose-500 text-slate-400 hover:text-white border border-slate-800 rounded-xl transition duration-200"
                      title="Hapus Log"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>

                  {/* Body text details */}
                  <div className="p-5 flex-1 flex flex-col">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <h4 className="font-bold text-base text-slate-100 group-hover:text-white transition duration-200 truncate">
                          {item.disease.replace(/_/g, " ")}
                        </h4>
                        <p className="text-[10px] text-slate-500 mt-1 font-medium">
                          Detected: {new Date(item.created_at).toLocaleDateString("id-ID", { day: "numeric", month: "short", year: "numeric" })}
                        </p>
                      </div>

                      <CheckCircle className="h-5 w-5 text-emerald-500 mt-0.5 shrink-0" />
                    </div>

                    {/* Matching Confidence progress bar */}
                    <div className="mt-6 space-y-1.5 flex-1">
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-slate-400 text-[10px] font-semibold">Confidence Score</span>
                        <span className="text-emerald-400 font-bold">{Math.round(item.confidence * 100)}%</span>
                      </div>
                      <div className="h-1.5 w-full bg-slate-900 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-emerald-500"
                          style={{ width: `${item.confidence * 100}%` }}
                        />
                      </div>
                    </div>

                    {/* Link button to Detection result page */}
                    <Link
                      href={`/detection?id=${item.id}`}
                      className="w-full flex items-center justify-center gap-1.5 py-2.5 border border-slate-800 hover:border-slate-700 hover:bg-slate-900 rounded-xl text-xs font-bold text-emerald-400 hover:text-emerald-300 transition mt-6"
                    >
                      View Detail
                      <ChevronRight className="h-4 w-4" />
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* ============================================== BOTTOM PAGINATION & FAB */}
          {!isLoading && filteredItems.length > 0 && (
            <div className="pt-6 border-t border-slate-800/50 flex flex-wrap items-center justify-between gap-4">
              {/* Load More Button */}
              <button
                onClick={() => loadHistory(currentPage + 1)}
                disabled={historyItems.length < 12}
                className="px-5 py-2.5 bg-slate-900 hover:bg-slate-800 border border-slate-800 text-xs font-bold rounded-xl text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed transition"
              >
                Load More History
              </button>

              {/* Numbers pagination selection */}
              <div className="flex items-center gap-1.5">
                <button
                  onClick={() => loadHistory(currentPage > 1 ? currentPage - 1 : 1)}
                  disabled={currentPage <= 1}
                  className="p-2 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-xl text-xs disabled:opacity-40 transition"
                >
                  &lt;
                </button>

                {paginationRange.map((pgNum) => (
                  <button
                    key={pgNum}
                    onClick={() => loadHistory(pgNum)}
                    className={cn(
                      "h-8 w-8 text-xs font-bold rounded-xl transition border",
                      currentPage === pgNum
                        ? "bg-emerald-600 border-emerald-500 text-white"
                        : "bg-slate-900 hover:bg-slate-800 border-slate-800 text-slate-400"
                    )}
                  >
                    {pgNum}
                  </button>
                ))}

                <button
                  onClick={() => loadHistory(currentPage + 1)}
                  disabled={historyItems.length < 12}
                  className="p-2 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-xl text-xs disabled:opacity-40 transition"
                >
                  &gt;
                </button>
              </div>
            </div>
          )}

        </div>
      </div>

      {/* Floating Action Button (FAB) on bottom right for mobile/scrolling scans */}
      <Link
        href="/detection"
        className="fixed bottom-6 right-6 h-14 w-14 rounded-full bg-emerald-600 hover:bg-emerald-500 text-white shadow-xl shadow-emerald-600/35 hover:scale-105 active:scale-95 flex items-center justify-center transition duration-200 z-40 border border-emerald-500"
        title="Mulai Scan Baru"
      >
        <Camera className="h-6 w-6" />
      </Link>

    </div>
  );
}
