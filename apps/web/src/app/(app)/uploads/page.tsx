"use client";

import * as React from "react";
import { useCallback, useState } from "react";
import { UploadIcon } from "@radix-ui/react-icons";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { GsapBridge } from "@/components/ui/gsap-bridge";
import { useGenerateUploadUrl, uploadFile } from "@/hooks/use-uploads";
import { AppPageFrame } from "@/components/layout/AppPageFrame";
import { AppPageSection } from "@/components/layout/AppPageSection";
import { AppEmptyState } from "@/components/layout/AppEmptyState";

export default function UploadsPage(): React.ReactElement {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dropActive, setDropActive] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const generateUploadUrl = useGenerateUploadUrl();

  const handleFile = useCallback((file: File | null) => {
    setSelectedFile(file);
    setStatus(null);
  }, []);

  const handleDrop = useCallback((event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setDropActive(false);
    const [file] = Array.from(event.dataTransfer.files);
    handleFile(file ?? null);
  }, [handleFile]);

  const handleUpload = async () => {
    if (!selectedFile) return;
    setUploading(true);
    setStatus(null);
    try {
      const response = await generateUploadUrl.mutateAsync({
        filename: selectedFile.name,
        contentType: selectedFile.type || "application/octet-stream",
      }) as { uploadUrl: string; key: string };
      await uploadFile(selectedFile, response.uploadUrl);
      setStatus(`Uploaded ${selectedFile.name} to ${response.key}`);
      setSelectedFile(null);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  return (
    <AppPageFrame
      eyebrow="Asset Repository"
      title="Uploads"
      description="S3-backed file uploads through the live backend."
    >
      <GsapBridge stagger={true} className="space-y-6">
        <AppPageSection>
          <div
            onDragOver={(event) => {
              event.preventDefault();
              setDropActive(true);
            }}
            onDragLeave={() => setDropActive(false)}
            onDrop={handleDrop}
            className={cn(
              "border-2 border-dashed p-12 flex flex-col items-center justify-center gap-4 transition-all duration-300 rounded-[var(--radius-lg)]",
              dropActive
                ? "border-[var(--primary)] bg-[var(--amber-wash)]"
                : "border-[var(--border)] bg-[var(--paper-50)] hover:border-[var(--paper-400)]",
            )}
          >
            <div className={cn(
              "w-12 h-12 rounded-full border flex items-center justify-center transition-colors",
              dropActive ? "border-[var(--primary)] bg-[var(--amber-wash)]" : "border-[var(--border)] bg-[var(--paper-150)]",
            )}>
              <UploadIcon className={cn("w-6 h-6", dropActive ? "text-[var(--primary)]" : "text-[var(--ink-400)]")} />
            </div>
            <div className="text-center space-y-2">
              <p className="text-[var(--ink-900)] font-medium text-sm uppercase tracking-tight">
                Drop an asset here or choose a file
              </p>
              <p className="text-[var(--ink-400)] text-[10px] font-mono uppercase tracking-widest">
                S3-backed upload through the live backend
              </p>
              <input
                type="file"
                className="mx-auto block text-xs"
                onChange={(event) => handleFile(event.target.files?.[0] ?? null)}
              />
            </div>
          </div>
        </AppPageSection>

        <AppPageSection title="Upload status">
          <div className="space-y-3">
            <p className="text-sm text-[var(--ink-500)]">
              {selectedFile ? `Selected: ${selectedFile.name}` : "No file selected yet."}
            </p>
            {status && <p className="text-sm">{status}</p>}
            <Button onClick={handleUpload} disabled={!selectedFile || uploading || generateUploadUrl.isPending}>
              {uploading || generateUploadUrl.isPending ? "Uploading..." : "Upload file"}
            </Button>
          </div>
        </AppPageSection>
      </GsapBridge>
    </AppPageFrame>
  );
}

function cn(...classes: (string | false | undefined)[]) {
  return classes.filter(Boolean).join(" ");
}
