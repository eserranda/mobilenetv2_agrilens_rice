"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Leaf, ArrowRight, ShieldAlert, CheckCircle } from "lucide-react";
import { registerUser } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (password !== confirmPassword) {
      setError("Kata sandi dan konfirmasi kata sandi tidak cocok.");
      return;
    }

    setLoading(true);
    try {
      await registerUser(username, password);
      setSuccess(true);
      setTimeout(() => {
        router.push("/login");
      }, 1500);
    } catch (err: any) {
      setError(err.message || "Gagal melakukan registrasi akun.");
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 bg-gradient-to-b from-emerald-100/60 via-white to-slate-100 px-6 py-12 text-slate-800">
      <div className="max-w-md w-full bg-white rounded-3xl border border-slate-100 p-8 shadow-xl shadow-slate-200/80 space-y-6">
        
        {/* Header */}
        <div className="text-center space-y-2">
          <Link href="/" className="inline-flex items-center gap-2.5 mx-auto">
            <div className="h-10 w-10 rounded-xl bg-emerald-600/10 border border-emerald-500/20 flex items-center justify-center text-emerald-600">
              <Leaf className="h-5.5 w-5.5 fill-current" />
            </div>
          </Link>
          <h2 className="text-2xl font-black text-slate-900 tracking-tight">Daftar Akun Baru</h2>
          <p className="text-xs text-slate-500">Mulai bergabung dengan platform presisi AgriLens Pro</p>
        </div>

        {/* Message Banner */}
        {error && (
          <div className="flex items-center gap-2.5 p-4 rounded-2xl bg-rose-50 border border-rose-100 text-rose-700 text-xs font-medium">
            <ShieldAlert className="h-5 w-5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div className="flex items-center gap-2.5 p-4 rounded-2xl bg-emerald-50 border border-emerald-100 text-emerald-700 text-xs font-medium">
            <CheckCircle className="h-5 w-5 shrink-0" />
            <span>Registrasi akun sukses! Mengalihkan ke halaman masuk...</span>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-[11px] font-extrabold text-slate-400 tracking-wider uppercase">Nama Pengguna</label>
            <input
              type="text"
              required
              disabled={loading || success}
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Minimal 3 karakter..."
              className="w-full px-4 py-3 bg-slate-50 border border-slate-200 focus:border-emerald-500 focus:bg-white focus:outline-none rounded-xl text-sm transition duration-200"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-[11px] font-extrabold text-slate-400 tracking-wider uppercase">Kata Sandi</label>
            <input
              type="password"
              required
              disabled={loading || success}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Minimal 4 karakter"
              className="w-full px-4 py-3 bg-slate-50 border border-slate-200 focus:border-emerald-500 focus:bg-white focus:outline-none rounded-xl text-sm transition duration-200"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-[11px] font-extrabold text-slate-400 tracking-wider uppercase">Konfirmasi Kata Sandi</label>
            <input
              type="password"
              required
              disabled={loading || success}
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Masukkan ulang kata sandi..."
              className="w-full px-4 py-3 bg-slate-50 border border-slate-200 focus:border-emerald-500 focus:bg-white focus:outline-none rounded-xl text-sm transition duration-200"
            />
          </div>

          <button
            type="submit"
            disabled={loading || success}
            className="w-full py-3.5 bg-emerald-600 hover:bg-emerald-500 active:bg-emerald-700 disabled:bg-slate-200 disabled:text-slate-400 text-white rounded-xl text-sm font-bold flex items-center justify-center gap-2 transition duration-200 shadow-md shadow-emerald-600/10 mt-6"
          >
            {loading ? "Mendaftarkan..." : "Daftar Akun"}
            <ArrowRight className="h-4.5 w-4.5" />
          </button>
        </form>

        {/* Login Link */}
        <div className="text-center pt-4 border-t border-slate-100">
          <p className="text-xs text-slate-500">
            Sudah memiliki akun?{" "}
            <Link href="/login" className="font-bold text-emerald-600 hover:text-emerald-500 transition">
              Masuk Sekarang
            </Link>
          </p>
        </div>

      </div>
    </div>
  );
}
