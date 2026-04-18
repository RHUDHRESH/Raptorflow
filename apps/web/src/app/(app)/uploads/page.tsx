"use client";

import * as React from "react";
import { useCallback, useState } from "react";
import { 
  UploadIcon, 
  FileIcon, 
  ImageIcon, 
  FileTextIcon, 
  ArchiveIcon, 
  TrashIcon, 
  DownloadIcon,
  MagnifyingGlassIcon,
  ViewGridIcon,
  ViewHorizontalIcon
} from "@radix-ui/react-icons";
import { cn } from "@/lib/cn";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { GsapBridge } from "@/components/ui/gsap-bridge";

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: string;
  uploadedAt: string;
  status: "uploading" | "done" | "error";
  progress?: number;
  url?: string;
}

const MOCK_ASSETS: UploadedFile[] = [
  { id: "f1", name: "Q2_Strategic_Objective.pdf", size: 245760, type: "application/pdf", uploadedAt: "2025-04-10T09:00:00Z", status: "done", url: "#" },
  { id: "f2", name: "Identity_Core_v3.docx", size: 184320, type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document", uploadedAt: "2025-04-09T14:30:00Z", status: "done", url: "#" },
  { id: "f3", name: "Market_Scan_01.png", size: 892416, type: "image/png", uploadedAt: "2025-04-08T11:15:00Z", status: "done", url: "#" },
  { id: "f4", name: "LinkedIn_Creative_Draft.docx", size: 43520, type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document", uploadedAt: "2025-04-07T16:45:00Z", status: "done", url: "#" },
  { id: "f5", name: "Pitch_Deck_Final.pptx", size: 3145728, type: "application/vnd.openxmlformats-officedocument.presentationml.presentation", uploadedAt: "2025-04-05T10:00:00Z", status: "done", url: "#" },
];

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function FileIconComponent({ type }: { type: string }) {
  if (type.startsWith("image/")) return <ImageIcon className="w-4 h-4" />;
  if (type.includes("pdf")) return <FileTextIcon className="w-4 h-4" />;
  if (type.includes("word") || type.includes("document")) return <FileIcon className="w-4 h-4" />;
  return <ArchiveIcon className="w-4 h-4" />;
}

export default function UploadsPage(): React.ReactElement {
  const [files, setFiles] = useState<UploadedFile[]>(MOCK_ASSETS);
  const [view, setView] = useState<"grid" | "list">("grid");
  const [search, setSearch] = useState("");
  const [dragging, setDragging] = useState(false);

  const onFiles = (newFiles: File[]) => {
     // Implementation flow would go here
     console.log("Files received:", newFiles);
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const files = Array.from(e.dataTransfer.files);
    if (files.length) onFiles(files);
  }, []);

  return (
    <div className="flex flex-col gap-10 py-2">
      <GsapBridge stagger={true}>
        {/* Header */}
        <header className="gsap-reveal flex items-end justify-between border-b-2 border-[var(--foreground)] pb-8">
          <div>
            <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.2em", color: "var(--muted-foreground)", marginBottom: 8 }}>
              Asset Repository // L1_STORAGE
            </p>
            <h1 style={{ fontFamily: "'DM Serif Display', serif", fontSize: 40, lineHeight: 1, margin: 0 }}>
              Asset Ledger
            </h1>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right hidden md:block">
              <p className="font-mono text-[8px] text-zinc-600 uppercase tracking-widest">Storage Efficiency</p>
              <p className="text-sm font-bold text-white">99.4%</p>
            </div>
            <Button className="h-10 px-6 bg-[var(--foreground)] text-[var(--background)] font-bold uppercase tracking-widest text-[10px] rounded-none">
              <UploadIcon className="w-4 h-4 mr-2" />
              Ingest Asset
            </Button>
          </div>
        </header>

        {/* Upload Zone */}
        <div 
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
          className={cn(
            "gsap-reveal border-2 border-dashed p-12 flex flex-col items-center justify-center gap-4 transition-all duration-300",
            dragging ? "border-amber-500 bg-amber-500/5" : "border-zinc-800 bg-zinc-900/20 hover:border-zinc-700"
          )}
        >
          <div className="w-12 h-12 rounded-full border border-zinc-800 flex items-center justify-center bg-zinc-900">
             <UploadIcon className={cn("w-6 h-6 transition-colors", dragging ? "text-amber-500" : "text-zinc-600")} />
          </div>
          <div className="text-center">
             <p className="text-white font-medium text-sm mb-1 uppercase tracking-tight">Drop tactical assets to ingest</p>
             <p className="text-zinc-600 text-[10px] font-mono uppercase tracking-widest">Max file size: 512MB // PDF, PNG, DOCX, PPTX</p>
          </div>
        </div>

        {/* Controls */}
        <div className="gsap-reveal flex flex-wrap items-center justify-between gap-6 border-b border-zinc-900 pb-6">
           <div className="flex items-center gap-2">
              <div className="relative">
                 <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-600" />
                 <input 
                    type="text" 
                    placeholder="Search ledger..."
                    className="h-10 pl-10 pr-4 bg-zinc-900/50 border border-zinc-800 text-[11px] font-mono text-white focus:outline-none focus:border-zinc-600 w-64 uppercase tracking-widest"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                 />
              </div>
              <div className="flex border border-zinc-800 h-10">
                 <button 
                    onClick={() => setView("grid")}
                    className={cn("px-3 transition-colors", view === "grid" ? "bg-zinc-800 text-white" : "text-zinc-600 hover:text-zinc-400")}
                 >
                    <ViewGridIcon className="w-4 h-4" />
                 </button>
                 <button 
                    onClick={() => setView("list")}
                    className={cn("px-3 border-l border-zinc-800 transition-colors", view === "list" ? "bg-zinc-800 text-white" : "text-zinc-600 hover:text-zinc-400")}
                 >
                    <ViewHorizontalIcon className="w-4 h-4" />
                 </button>
              </div>
           </div>
           <div className="flex gap-4">
              <div className="flex items-center gap-2 text-[10px] font-mono text-zinc-600 uppercase tracking-[0.2em]">
                 <span className="h-1.5 w-1.5 rounded-full bg-amber-500" />
                 {files.length} Assets Loaded
              </div>
           </div>
        </div>

        {/* Results */}
        {view === "grid" ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {files.map((file) => (
              <div key={file.id} className="gsap-reveal border border-zinc-800 bg-[#0d0d0d] p-5 group hover:border-zinc-600 transition-all flex flex-col h-[180px]">
                 <div className="flex items-start justify-between mb-4">
                    <div className="p-2 border border-zinc-800 bg-zinc-900/50 group-hover:border-amber-500/50 transition-colors">
                       <FileIconComponent type={file.type} />
                    </div>
                    <Badge variant="outline" className="text-[8px] font-mono tracking-widest uppercase border-zinc-800">
                       {file.type.split('/')[1]?.toUpperCase() || "BIN"}
                    </Badge>
                 </div>
                 <h3 className="text-sm font-bold text-white mb-2 line-clamp-1 group-hover:text-amber-500 transition-colors">{file.name}</h3>
                 <p className="font-mono text-[9px] text-zinc-600 mt-auto">{formatBytes(file.size)} // {new Date(file.uploadedAt).toLocaleDateString()}</p>
                 <div className="flex gap-2 mt-4 pt-4 border-t border-zinc-900 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button className="text-[10px] font-mono font-bold uppercase tracking-widest text-zinc-400 hover:text-white flex items-center gap-1">
                       <DownloadIcon className="w-3 h-3" /> Get
                    </button>
                    <button className="text-[10px] font-mono font-bold uppercase tracking-widest text-red-500/50 hover:text-red-500 flex items-center gap-1 ml-auto">
                       <TrashIcon className="w-3 h-3" /> Wipe
                    </button>
                 </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="gsap-reveal border border-zinc-800 divide-y divide-zinc-900 bg-[#0d0d0d]">
             {files.map((file) => (
               <div key={file.id} className="p-4 flex items-center justify-between group hover:bg-white/[0.02]">
                  <div className="flex items-center gap-4">
                     <FileIconComponent type={file.type} />
                     <div>
                        <p className="text-sm font-medium text-white group-hover:text-amber-500 transition-colors uppercase tracking-tight">{file.name}</p>
                        <p className="text-[9px] font-mono text-zinc-600 uppercase tracking-widest">{formatBytes(file.size)} // {file.type}</p>
                     </div>
                  </div>
                  <div className="flex items-center gap-6">
                     <span className="text-[10px] font-mono text-zinc-700 uppercase tracking-widest hidden lg:block">Uploaded: {new Date(file.uploadedAt).toLocaleDateString()}</span>
                     <div className="flex gap-3">
                        <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-zinc-600 hover:text-white">
                           <DownloadIcon />
                        </Button>
                        <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-zinc-600 hover:text-red-500">
                           <TrashIcon />
                        </Button>
                     </div>
                  </div>
               </div>
             ))}
          </div>
        )}
      </GsapBridge>
    </div>
  );
}
