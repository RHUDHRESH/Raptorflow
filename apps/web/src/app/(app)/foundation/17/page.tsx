"use client";

import React, { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { Check, X, Upload, Plus } from "lucide-react";
import { useFoundationStore } from "@/state/foundation-store";
import { cn } from "@/lib/utils";

interface AssetFile {
  name: string;
  size: string;
}

interface AssetType {
  id: string;
  label: string;
  accepts: string;
  checked: boolean;
  files: AssetFile[];
}

/**
 * Foundation Screen 17: Existing Assets and Social Handles
 * Inventories existing brand collateral and social presence.
 */
export default function FoundationStep17() {
  const router = useRouter();
  const { getToken } = useAuth();
  const { sectionData, setSectionData, setStep } = useFoundationStore();

  const [assets, setAssets] = useState<AssetType[]>([
    { id: "brand", label: "Brand guidelines & logo files", accepts: ".pdf,.ai,.png,.jpg,.zip", checked: false, files: [] },
    { id: "ads", label: "Past advertising creative", accepts: ".png,.jpg,.mp4,.zip", checked: false, files: [] },
    { id: "testimonials", label: "Customer testimonials", accepts: ".pdf,.txt,.docx", checked: false, files: [] },
    { id: "case_studies", label: "Case studies", accepts: ".pdf,.docx", checked: false, files: [] },
    { id: "product", label: "Product photos or video", accepts: ".png,.jpg,.mp4", checked: false, files: [] },
    { id: "email", label: "Email templates", accepts: ".html,.zip", checked: false, files: [] },
  ]);

  const [socialHandles, setSocialHandles] = useState({
    instagram: "",
    linkedin: "",
    facebook: "",
    youtube: "",
    twitter: "",
    whatsapp: "",
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [activeAssetId, setActiveAssetId] = useState<string | null>(null);

  useEffect(() => {
    setStep(17);
    const existing = sectionData.existing_assets;
    if (existing) {
      if (existing.socialHandles) setSocialHandles(existing.socialHandles);
      if (existing.assets) {
        setAssets(prev => prev.map(a => {
          const ext = existing.assets.find((ea: any) => ea.id === a.id);
          return ext ? { ...a, ...ext } : a;
        }));
      }
    }
  }, [setStep, sectionData]);

  const toggleAsset = (id: string) => {
    setAssets(prev => prev.map(a => a.id === id ? { ...a, checked: !a.checked } : a));
  };

  const handleFileUploadClick = (id: string) => {
    setActiveAssetId(id);
    if (fileInputRef.current) fileInputRef.current.click();
  };

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !activeAssetId) return;

    const sizeStr = (file.size / (1024 * 1024)).toFixed(1) + " MB";
    const newFile = { name: file.name, size: sizeStr };

    setAssets(prev => prev.map(a => {
      if (a.id === activeAssetId) {
        if (a.files.length >= 3) return a;
        return { ...a, files: [...a.files, newFile] };
      }
      return a;
    }));
    e.target.value = ""; // Reset
  };

  const removeFile = (assetId: string, fileName: string) => {
    setAssets(prev => prev.map(a => 
      a.id === assetId ? { ...a, files: a.files.filter(f => f.name !== fileName) } : a
    ));
  };

  const handleContinue = async () => {
    setIsSubmitting(true);
    const data = {
      assets: assets.map(a => ({ id: a.id, label: a.label, checked: a.checked, fileNames: a.files.map(f => f.name) })),
      socialHandles
    };

    try {
      const token = await getToken();
      setSectionData("existing_assets", data);

      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/foundation/section/existing_assets`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      });

      router.push("/foundation/18");
    } catch (err) {
      console.error("[Foundation17] Error:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col items-center px-6 pt-20 pb-24 min-h-screen bg-[#FBF8F2]">
      <div className="w-full max-w-[640px] space-y-10">
        
        {/* HEADER */}
        <div className="space-y-2">
          <h1 className="text-3xl font-bold text-[#2A2622]">What do you already have?</h1>
          <p className="text-base text-[#6B655E]">Your AI team will build on what exists, not duplicate it.</p>
        </div>

        {/* ASSET CHECKLIST */}
        <div className="space-y-3">
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={onFileChange} 
            className="hidden" 
            accept={assets.find(a => a.id === activeAssetId)?.accepts}
          />
          {assets.map((asset) => (
            <div key={asset.id} className="space-y-2">
              <div 
                onClick={() => toggleAsset(asset.id)}
                className={cn(
                  "flex items-center justify-between p-4 rounded-xl border transition-all duration-300 cursor-pointer",
                  asset.checked ? "bg-[#262626] border-[#D5CBC0] shadow-lg" : "bg-[#FBF8F2] border-[#E5DED4] hover:border-[#D5CBC0]"
                )}
              >
                <div className="flex items-center gap-4">
                  <div className={cn(
                    "w-5 h-5 rounded-sm border-2 flex items-center justify-center transition-all",
                    asset.checked ? "bg-[#f59e0b] border-[#f59e0b]" : "border-[#D5CBC0]"
                  )}>
                    {asset.checked && <Check className="w-3.5 h-3.5 text-black" />}
                  </div>
                  <span className={cn("text-sm font-medium transition-colors", asset.checked ? "text-[#2A2622]" : "text-[#6B655E]")}>
                    {asset.label}
                  </span>
                  {asset.files.length > 0 && asset.checked && (
                    <span className="bg-[#f59e0b]/10 text-[#f59e0b] px-2 py-0.5 rounded-full text-[10px] font-bold">
                      {asset.files.length}
                    </span>
                  )}
                </div>

                {asset.checked && asset.files.length < 3 && (
                  <button
                    onClick={(e) => { e.stopPropagation(); handleFileUploadClick(asset.id); }}
                    className="flex items-center gap-1.5 px-3 py-1 border border-[#D5CBC0] rounded-lg text-xs text-[#6B655E] hover:text-[#2A2622] hover:border-[#D5CBC0] transition-all font-bold uppercase tracking-wider"
                  >
                    <Upload className="w-3 h-3" />
                    Upload
                  </button>
                )}
              </div>

              {/* UPLOADED FILES LIST */}
              {asset.checked && asset.files.length > 0 && (
                <div className="pl-12 flex flex-col gap-1 text-xs text-[#6B655E] animate-in fade-in slide-in-from-top-1 duration-200">
                  {asset.files.map((file) => (
                    <div key={file.name} className="flex items-center gap-2">
                      <span className="truncate max-w-[200px]">{file.name}</span>
                      <span className="text-[10px] opacity-60">· {file.size}</span>
                      <button 
                        onClick={() => removeFile(asset.id, file.name)}
                        className="p-1 hover:text-red-400 transition-colors"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* SOCIAL HANDLES */}
        <div className="pt-6 border-t border-[#E5DED4] space-y-8">
          <div className="space-y-1">
            <h2 className="text-lg font-medium text-[#2A2622]">Social media and ad accounts</h2>
            <p className="text-sm text-[#6B655E]">These get added to your monitoring stack immediately.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { id: "instagram", label: "Instagram", icon: "📸", placeholder: "@yourbrand" },
              { id: "linkedin", label: "LinkedIn", icon: "💼", placeholder: "linkedin.com/company/brand" },
              { id: "facebook", label: "Facebook", icon: "👍", placeholder: "facebook.com/yourbrand" },
              { id: "youtube", label: "YouTube", icon: "📹", placeholder: "youtube.com/@yourbrand" },
              { id: "twitter", label: "Twitter / X", icon: "🐦", placeholder: "@yourbrand" },
              { id: "whatsapp", label: "WhatsApp", icon: "💬", placeholder: "+91 XXXXX XXXXX" },
            ].map((p) => (
              <div key={p.id} className="space-y-1.5">
                <label className="text-[10px] font-bold uppercase tracking-widest text-[#6B655E] flex items-center gap-2">
                  <span>{p.icon}</span>
                  {p.label}
                </label>
                <input
                  className="w-full bg-[#FBF8F2] border border-[#E5DED4] rounded-lg px-4 py-2.5 text-sm text-[#2A2622] placeholder:text-[#9A948C] focus:outline-none focus:border-[#f59e0b] focus:bg-[#262626] transition-all"
                  placeholder={p.placeholder}
                  value={(socialHandles as any)[p.id]}
                  onChange={(e) => setSocialHandles({ ...socialHandles, [p.id]: e.target.value })}
                />
              </div>
            ))}
          </div>
        </div>

        {/* CTA */}
        <button
          onClick={handleContinue}
          disabled={isSubmitting}
          className="w-full bg-[#f59e0b] hover:bg-[#d97706] disabled:bg-[#D5CBC0] disabled:opacity-50 text-black font-bold rounded-lg py-4 transition-all mt-8"
        >
          {isSubmitting ? "Processing Assets..." : "Continue"}
        </button>

      </div>
    </div>
  );
}
