"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Users, Loader2, ShieldAlert, Calendar, UserCheck, Trash2 } from "lucide-react";
import { getAllUsers, deleteUser, UserResponse } from "@/lib/api";
import Header from "@/components/Header";

export default function UsersAdminPage() {
  const router = useRouter();
  const [users, setUsers] = useState<UserResponse[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [currentUsername, setCurrentUsername] = useState<string>("");

  useEffect(() => {
    // Check if user is logged in and is admin
    const token = localStorage.getItem("agrilens_token");
    const role = localStorage.getItem("agrilens_role");
    const name = localStorage.getItem("agrilens_username") || "";

    if (!token) {
      router.push("/login");
      return;
    }

    if (role !== "admin") {
      router.push("/detection");
      return;
    }

    setCurrentUsername(name);
    loadUsers();
  }, [router]);

  const handleDeleteUser = async (userId: number, usernameToDelete: string) => {
    if (usernameToDelete === currentUsername) {
      alert("Anda tidak dapat menghapus akun Anda sendiri.");
      return;
    }

    const confirmDelete = window.confirm(
      `Apakah Anda yakin ingin menghapus pengguna "${usernameToDelete}"? Semua riwayat diagnosa milik pengguna ini akan tetap disimpan namun diubah statusnya menjadi anonim.`
    );
    if (!confirmDelete) {
      return;
    }

    try {
      setError(null);
      await deleteUser(userId);
      loadUsers(); // Refresh list after successful delete
    } catch (err: any) {
      setError(err.message || "Gagal menghapus pengguna.");
    }
  };

  const loadUsers = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getAllUsers();
      setUsers(data);
    } catch (err: any) {
      setError(err.message || "Gagal mengambil daftar pengguna.");
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString("id-ID", {
        day: "numeric",
        month: "long",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch (e) {
      return dateStr;
    }
  };

  return (
    <div className="flex-1 flex flex-col min-h-0 bg-slate-900 text-slate-100">
      
      {/* Header */}
      <Header>
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
            <Users className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-lg font-black tracking-tight text-white">Kelola Pengguna</h1>
            <p className="text-xs text-slate-400">Daftar akun yang terdaftar dalam sistem AgriLens Pro</p>
          </div>
        </div>
      </Header>

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto p-6 space-y-6">
        
        {error && (
          <div className="flex items-center gap-3 p-4 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm">
            <ShieldAlert className="h-5 w-5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {isLoading ? (
          <div className="flex-1 flex flex-col items-center justify-center py-24 space-y-3">
            <Loader2 className="h-8 w-8 text-emerald-400 animate-spin" />
            <p className="text-xs text-slate-400 font-medium">Memuat data pengguna...</p>
          </div>
        ) : (
          <div className="bg-slate-950/40 border border-slate-900 rounded-3xl overflow-hidden shadow-2xl">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-slate-900 bg-slate-950/60">
                    <th className="px-6 py-4.5 text-xs font-bold text-slate-400 uppercase tracking-wider">ID</th>
                    <th className="px-6 py-4.5 text-xs font-bold text-slate-400 uppercase tracking-wider">Nama Pengguna</th>
                    <th className="px-6 py-4.5 text-xs font-bold text-slate-400 uppercase tracking-wider">Peran (Role)</th>
                    <th className="px-6 py-4.5 text-xs font-bold text-slate-400 uppercase tracking-wider">Tanggal Registrasi</th>
                    <th className="px-6 py-4.5 text-xs font-bold text-slate-400 uppercase tracking-wider text-right">Aksi</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-900/60">
                  {users.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="px-6 py-12 text-center text-xs text-slate-500 font-medium">
                        Tidak ada pengguna terdaftar yang ditemukan.
                      </td>
                    </tr>
                  ) : (
                    users.map((user) => (
                      <tr key={user.id} className="hover:bg-slate-900/20 transition duration-150">
                        <td className="px-6 py-4 text-xs font-semibold text-slate-500">#{user.id}</td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2.5">
                            <div className="h-8 w-8 rounded-lg bg-slate-900 flex items-center justify-center text-slate-300 font-bold text-xs">
                              {user.username.charAt(0).toUpperCase()}
                            </div>
                            <span className="text-sm font-bold text-white">{user.username}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <span
                            className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-bold ${
                              user.role === "admin"
                                ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/10"
                                : "bg-blue-500/10 text-blue-400 border border-blue-500/10"
                            }`}
                          >
                            <UserCheck className="h-3 w-3" />
                            {user.role === "admin" ? "Administrator" : "User"}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2 text-xs text-slate-400">
                            <Calendar className="h-3.5 w-3.5 text-slate-500" />
                            <span>{formatDate(user.created_at)}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-right">
                          <button
                            disabled={user.username === currentUsername}
                            onClick={() => handleDeleteUser(user.id, user.username)}
                            className="p-2 bg-slate-900/40 hover:bg-rose-500/10 hover:text-rose-400 hover:border-rose-500/20 active:bg-rose-500/20 disabled:opacity-30 disabled:hover:bg-transparent disabled:hover:text-slate-500 border border-transparent hover:border-rose-500/10 rounded-xl transition duration-150 text-slate-500"
                            title={user.username === currentUsername ? "Anda tidak dapat menghapus akun Anda sendiri" : "Hapus Pengguna"}
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
            <div className="p-4 bg-slate-950/60 border-t border-slate-900 flex items-center justify-between text-xs text-slate-500">
              <span>Menampilkan {users.length} pengguna terdaftar</span>
            </div>
          </div>
        )}

      </main>
    </div>
  );
}
