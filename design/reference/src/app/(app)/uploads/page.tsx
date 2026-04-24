"use client";

import type * as React from "react";
import { useCallback, useState } from "react";
import { RouteShell } from "@/components/layout/route-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/cn";
import { useGenerateUploadUrl, useDeleteUpload, uploadFile } from "@/hooks/use-uploads";
import { publicEnv } from "@/lib/env"; // # FIXED: use real upload flow instead of mock simulation

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: string;
  uploadedAt: string;
  status: "uploading" | "done" | "error";
  progress?: number;
  url?: string;
  key?: string;
}

const MOCK_ASSETS: UploadedFile[] = [
  { id: "f1", name: "Q2_Campaign_Brief.pdf", size: 245760, type: "application/pdf", uploadedAt: "2025-04-10T09:00:00Z", status: "done", url: "#" },
  { id: "f2", name: "Brand_Guidelines_v3.docx", size: 184320, type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document", uploadedAt: "2025-04-09T14:30:00Z", status: "done", url: "#" },
  { id: "f3", name: "Competitor_Screenshot_01.png", size: 892416, type: "image/png", uploadedAt: "2025-04-08T11:15:00Z", status: "done", url: "#" },
  { id: "f4", name: "LinkedIn_Post_Draft_v2.docx", size: 43520, type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document", uploadedAt: "2025-04-07T16:45:00Z", status: "done", url: "#" },
  { id: "f5", name: "Webinar_Slides_Final.pptx", size: 3145728, type: "application/vnd.openxmlformats-officedocument.presentationml.presentation", uploadedAt: "2025-04-05T10:00:00Z", status: "done", url: "#" },
];

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function getFileIcon(type: string) {
  if (type.startsWith("image/")) return "🖼";
  if (type.includes("pdf")) return "📄";
  if (type.includes("word") || type.includes("document")) return "📝";
  if (type.includes("presentation") || type.includes("pptx")) return "📊";
  return "📎";
}

function UploadZone({ onFiles }: { onFiles: (files: File[]) => void }) {
  const [dragging, setDragging] = useState(false);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const files = Array.from(e.dataTransfer.files);
    if (files.length) onFiles(files);
  }, [onFiles]);

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files ?? []);
    if (files.length) onFiles(files);
    e.target.value = "";
  }, [onFiles]);

  return (
    <label
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      className={cn(
        "flex flex-col items-center justify-center gap-4 rounded-2xl border-2 border-dashed p-10 transition-colors cursor-pointer",
        dragging ? "border-[var(--primary)] bg-[var(--primary)]/5" : "border-[var(--border)] bg-white/40 hover:bg-white/60"
      )}
    >
      <div className="text-4xl">📁</div>
      <div className="space-y-1 text-center">
        <p className="font-medium">Drop files here or click to browse</p>
        <p className="text-sm text-[var(--muted-foreground)]">
          PDF, DOCX, PNG, JPG, PPTX — up to 50 MB each
        </p>
      </div>
      <input
        type="file"
        multiple
        accept=".pdf,.docx,.doc,.png,.jpg,.jpeg,.pptx"
        onChange={handleChange}
        className="sr-only"
      />
      <Button type="button" variant="secondary" size="sm" onClick={() => {}}>
        Browse files
      </Button>
    </label>
  );
}

function FileCard({ file }: { file: UploadedFile }) {
  const [selected, setSelected] = useState(false);

  return (
    <div
      className={cn(
        "group relative flex items-start gap-4 rounded-2xl border border-[var(--border)] bg-white/70 p-4 transition-colors hover:bg-white",
        selected && "border-[var(--primary)] bg-[var(--primary)]/5"
      )}
    >
      <button
        type="button"
        onClick={() => setSelected(!selected)}
        className={cn(
          "mt-1 h-5 w-5 flex-shrink-0 rounded border-2 transition-colors",
          selected ? "border-[var(--primary)] bg-[var(--primary)]" : "border-[var(--border)]"
        )}
      />

      <div className="flex flex-1 items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <span className="mt-0.5 text-2xl">{getFileIcon(file.type)}</span>
          <div className="space-y-1">
            <p className="font-medium leading-snug">{file.name}</p>
            <p className="text-xs text-[var(--muted-foreground)]">
              {formatBytes(file.size)} · {new Date(file.uploadedAt).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}
            </p>
            {file.status === "uploading" && (
              <div className="mt-2 w-48 overflow-hidden rounded-full bg-[var(--muted)]">
                <div className="h-1.5 bg-[var(--primary)] transition-all" style={{ width: `${file.progress ?? 0}%` }} />
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          {file.status === "done" && <Badge className="bg-green-100 text-green-700 border-green-200">Uploaded</Badge>}
          {file.status === "uploading" && <Badge variant="outline">{file.progress}%</Badge>}
          {file.status === "error" && <Badge className="bg-red-100 text-red-700 border-red-200">Failed</Badge>}
          <Button size="sm" variant="ghost" className="opacity-0 group-hover:opacity-100" asChild>
            <a href={file.url} download={file.name} onClick={(e) => e.stopPropagation()}>
              ↓
            </a>
          </Button>
          <Button size="sm" variant="ghost" className="opacity-0 group-hover:opacity-100 text-red-500 hover:text-red-600">
            ✕
          </Button>
        </div>
      </div>
    </div>
  );
}

type ViewMode = "grid" | "list";
type FilterType = "all" | "document" | "image" | "presentation";

export default function UploadsPage(): React.ReactElement {
  const [files, setFiles] = useState<UploadedFile[]>(MOCK_ASSETS);
  const [view, setView] = useState<ViewMode>("grid");
  const [filter, setFilter] = useState<FilterType>("all");
  const [search, setSearch] = useState("");

  const generateUploadUrl = useGenerateUploadUrl();
  const deleteUpload = useDeleteUpload();

  const handleFiles = useCallback(async (newFiles: File[]) => {
    const uploadEntries: UploadedFile[] = newFiles.map((f, i) => ({
      id: `upload-${Date.now()}-${i}`,
      name: f.name,
      size: f.size,
      type: f.type,
      uploadedAt: new Date().toISOString(),
      status: "uploading",
      progress: 0,
    }));

    setFiles((prev) => [...uploadEntries, ...prev]);

    for (const file of uploadEntries) {
      try {
        if (publicEnv.offlineMode) {
          let progress = 0;
          const interval = setInterval(() => {
            progress += Math.random() * 25 + 10;
            if (progress >= 100) {
              progress = 100;
              clearInterval(interval);
              setFiles((prev) =>
                prev.map((f) => (f.id === file.id ? { ...f, status: "done", progress: 100 } : f))
              );
            } else {
              setFiles((prev) =>
                prev.map((f) => (f.id === file.id ? { ...f, progress: Math.round(progress) } : f))
              );
            }
          }, 300);
        } else {
          const urlResult = await generateUploadUrl.mutateAsync({ filename: file.name, contentType: file.type });
          await uploadFile(
            newFiles.find((f) => f.name === file.name)!,
            urlResult.uploadUrl,
            (percent) => {
              setFiles((prev) =>
                prev.map((f) => (f.id === file.id ? { ...f, progress: percent } : f))
              );
            }
          );
          setFiles((prev) =>
            prev.map((f) => (f.id === file.id ? { ...f, status: "done", progress: 100, key: urlResult.key, url: urlResult.uploadUrl } : f))
          );
        }
      } catch {
        setFiles((prev) =>
          prev.map((f) => (f.id === file.id ? { ...f, status: "error" } : f))
        );
      }
    }
  }, [generateUploadUrl]); // # FIXED: use real uploadFile() with XHR progress instead of mock setInterval simulation

  const filteredFiles = files.filter((f) => {
    if (filter === "document" && !f.type.includes("pdf") && !f.type.includes("word") && !f.type.includes("document")) return false;
    if (filter === "image" && !f.type.startsWith("image/")) return false;
    if (filter === "presentation" && !f.type.includes("presentation") && !f.type.includes("pptx")) return false;
    if (search && !f.name.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const selectedCount = files.filter((f) => f.type.includes("pdf") || f.type.includes("document")).length;

  return (
    <RouteShell
      eyebrow="Storage"
      title="Uploads"
      description="Upload, manage, and share files for your campaigns and foundation."
      tags={["s3", "assets", "storage"]}
    >
      <div className="flex flex-col gap-6">
        <UploadZone onFiles={handleFiles} />

        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex gap-2">
            {(["all", "document", "image", "presentation"] as FilterType[]).map((f) => (
              <Button
                key={f}
                size="sm"
                variant={filter === f ? "default" : "secondary"}
                onClick={() => setFilter(f)}
              >
                {f.charAt(0).toUpperCase() + f.slice(1)}
              </Button>
            ))}
          </div>
          <div className="flex items-center gap-3">
            <input
              type="search"
              placeholder="Search files..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="rounded-lg border border-[var(--border)] bg-white px-3 py-2 text-sm placeholder:text-[var(--muted-foreground)] focus:border-[var(--primary)] focus:outline-none focus:ring-1 focus:ring-[var(--ring)]"
            />
            <div className="flex rounded-lg border border-[var(--border)]">
              <button
                type="button"
                onClick={() => setView("grid")}
                className={cn("px-3 py-2 text-sm", view === "grid" ? "bg-[var(--muted)]" : "")}
              >
                ⊞
              </button>
              <button
                type="button"
                onClick={() => setView("list")}
                className={cn("px-3 py-2 text-sm", view === "list" ? "bg-[var(--muted)]" : "")}
              >
                ≡
              </button>
            </div>
          </div>
        </div>

        {filteredFiles.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-16 text-center">
              <p className="text-3xl">📂</p>
              <p className="mt-4 font-medium">No files found</p>
              <p className="mt-1 text-sm text-[var(--muted-foreground)]">
                {search ? `No files matching "${search}"` : "Drop files above to upload"}
              </p>
            </CardContent>
          </Card>
        ) : view === "grid" ? (
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {filteredFiles.map((file) => (
              <FileCard key={file.id} file={file} />
            ))}
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            {filteredFiles.map((file) => (
              <FileCard key={file.id} file={file} />
            ))}
          </div>
        )}
      </div>
    </RouteShell>
  );
}
