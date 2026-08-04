"use client";

import React, { useState, useEffect } from "react";
import { User, Settings } from "lucide-react";
import { getSetting, updateSetting } from "@/lib/api";
import { cn } from "@/lib/utils";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

interface HeaderProps {
  children?: React.ReactNode;      // Page-specific elements in the left/middle slot (e.g. tabs or search input)
  rightActions?: React.ReactNode;  // Page-specific buttons in the right slot (e.g. filters)
}

export default function Header({ children, rightActions }: HeaderProps) {
  const [openaiGuardrail, setOpenaiGuardrail] = useState<boolean>(true);
  const [isSettingsOpen, setIsSettingsOpen] = useState<boolean>(false);

  // Fetch setting on load
  useEffect(() => {
    fetchGuardrailSetting();
  }, []);

  const fetchGuardrailSetting = async () => {
    try {
      const data = await getSetting("openai_guardrail");
      setOpenaiGuardrail(data.value === "true");
    } catch (err) {
      console.error("Failed to load setting:", err);
    }
  };

  const handleGuardrailToggle = async (value: boolean) => {
    setOpenaiGuardrail(value);
    try {
      await updateSetting("openai_guardrail", value ? "true" : "false");
    } catch (err) {
      console.error("Failed to save setting:", err);
    }
  };

  return (
    <header className="hidden md:flex h-16 border-b border-slate-900 px-6 items-center justify-between shrink-0 bg-slate-950/50 z-10 w-full">
      {/* Left/Middle Slot */}
      <div className="flex items-center gap-6 flex-1 min-w-0">
        {children}
      </div>

      {/* Right Actions Slot, Settings Gear, & Avatar */}
      <div className="flex items-center gap-4 shrink-0 ml-4">
        {rightActions}

        {/* Global Settings Dialog */}
        <Dialog open={isSettingsOpen} onOpenChange={setIsSettingsOpen}>
          <DialogTrigger render={
            <button className="text-slate-400 hover:text-white transition p-1.5 hover:bg-slate-900 rounded-lg" title="Pengaturan">
              <Settings className="h-5 w-5" />
            </button>
          } />
          <DialogContent className="sm:max-w-md bg-slate-900 border border-slate-800 text-white rounded-3xl p-6">
            <DialogHeader>
              <DialogTitle className="text-lg font-bold text-slate-200">Pengaturan Analisis</DialogTitle>
              <DialogDescription className="text-xs text-slate-400 mt-1">
                Konfigurasi bagaimana model AgriLens Pro memproses dan memvalidasi gambar.
              </DialogDescription>
            </DialogHeader>

            {/* Switch Toggle for OpenAI Verification */}
            <div className="my-6">
              <div className="flex items-center justify-between p-4 border rounded-2xl bg-slate-950/20 border-slate-800 hover:border-slate-800 transition duration-300">
                <div className="flex flex-col pr-4">
                  <span className="text-xs font-bold text-slate-200">Verifikasi Gambar (OpenAI Vision Guardrail)</span>
                  <span className="text-[10px] text-slate-500 mt-1 leading-relaxed">
                    Menyaring gambar yang bukan daun padi (seperti foto manusia, hewan, makanan) sebelum inferensi dijalankan untuk menghindari salah klasifikasi.
                  </span>
                </div>

                {/* Switch Toggle Button */}
                <button
                  type="button"
                  role="switch"
                  aria-checked={openaiGuardrail}
                  onClick={() => handleGuardrailToggle(!openaiGuardrail)}
                  className={cn(
                    "relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-emerald-500/25 focus:ring-offset-2 focus:ring-offset-slate-900",
                    openaiGuardrail ? "bg-emerald-600" : "bg-slate-800"
                  )}
                >
                  <span
                    className={cn(
                      "pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow-lg ring-0 transition duration-200 ease-in-out",
                      openaiGuardrail ? "translate-x-5" : "translate-x-0"
                    )}
                  />
                </button>
              </div>
            </div>

            <DialogFooter className="border-t border-slate-800/60 pt-4 flex gap-2">
              <DialogClose render={
                <Button variant="outline" className="w-full py-2.5 bg-slate-950/40 border-slate-800 hover:bg-slate-900 rounded-xl text-xs text-slate-400 font-bold hover:text-white transition">
                  Tutup
                </Button>
              } />
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* User Profile Avatar */}
        {/* <div className="h-8 w-8 rounded-full bg-slate-800 border border-slate-700 overflow-hidden flex items-center justify-center shrink-0">
          <User className="h-4.5 w-4.5 text-slate-400" />
        </div> */}
      </div>
    </header>
  );
}
