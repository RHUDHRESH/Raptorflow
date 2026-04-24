"use client";

import * as React from "react";
import { useCallback, useState } from "react";
import { UploadIcon } from "@radix-ui/react-icons";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { GsapBridge } from "@/components/ui/gsap-bridge";
import { useGenerateUploadUrl, uploadFile } from "@/hooks/use-uploads";

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
      });
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
    <div className="flex flex-col gap-6 py-2">
      <GsapBridge stagger={true}>
        <header className="gsap-reveal flex items-end justify-between border-b-2 border-[var(--foreground)] pb-8">
          <div>
            <p
              style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: 9,
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.2em",
                color: "var(--muted-foreground)",
                marginBottom: 8,
              }}
            >
              Asset Repository // Live Uploads
            </p>
            <h1 style={{ fontFamily: "'DM Serif Display', serif", fontSize: 40, lineHeight: 1, margin: 0 }}>
              Uploads
            </h1>
          </div>
        </header>

        <div
          onDragOver={(event) => {
            event.preventDefault();
            setDropActive(true);
          }}
          onDragLeave={() => setDropActive(false)}
          onDrop={handleDrop}
          className={`gsap-reveal border-2 border-dashed p-12 flex flex-col items-center justify-center gap-4 transition-all duration-300 ${
            dropActive ? "border-[#D97757] bg-[#FBE9DE]" : "border-[#E5DED4] bg-[#F5F0E8]/20 hover:border-[#D5CBC0]"
          }`}
        >
          <div className="w-12 h-12 rounded-full border border-[#E5DED4] flex items-center justify-center bg-[#F5F0E8]">
            <UploadIcon className={dropActive ? "w-6 h-6 text-[#D97757]" : "w-6 h-6 text-[#9A948C]"} />
          </div>
          <div className="text-center space-y-2">
            <p className="text-[#2A2622] font-medium text-sm uppercase tracking-tight">
              Drop an asset here or choose a file
            </p>
            <p className="text-[#9A948C] text-[10px] font-mono uppercase tracking-widest">
              S3-backed upload through the live backend
            </p>
            <input
              type="file"
              className="mx-auto block text-xs"
              onChange={(event) => handleFile(event.target.files?.[0] ?? null)}
            />
          </div>
        </div>

        <Card className="gsap-reveal">
          <CardHeader>
            <CardTitle className="text-base">Upload status</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="text-sm text-[var(--muted-foreground)]">
              {selectedFile ? `Selected: ${selectedFile.name}` : "No file selected yet."}
            </p>
            {status && <p className="text-sm">{status}</p>}
            <Button onClick={handleUpload} disabled={!selectedFile || uploading || generateUploadUrl.isPending}>
              {uploading || generateUploadUrl.isPending ? "Uploading…" : "Upload file"}
            </Button>
          </CardContent>
        </Card>

        <Card className="gsap-reveal border-amber-200 bg-amber-50/50">
          <CardHeader>
            <CardTitle className="text-base">What this page does now</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-amber-800">
            <p>This page now generates a presigned S3 upload URL and sends the file directly to storage.</p>
            <p>Asset listing remains backend-driven; do not reintroduce local mock ledgers here.</p>
          </CardContent>
        </Card>
      </GsapBridge>
    </div>
  );
}
