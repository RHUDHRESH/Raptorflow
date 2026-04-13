"use client";

import { useMutation } from "@tanstack/react-query";
import { uploadsApi } from "@/lib/api";

export function useGenerateUploadUrl() {
  return useMutation({
    mutationFn: ({ filename, contentType }: { filename: string; contentType: string }) =>
      uploadsApi.generateUploadUrl({ filename, contentType }),
  });
}

export function useGenerateDownloadUrl() {
  return useMutation({
    mutationFn: (key: string) => uploadsApi.generateDownloadUrl(key),
  });
}

export function useDeleteUpload() {
  return useMutation({
    mutationFn: (key: string) => uploadsApi.deleteUpload(key),
  });
}

export function useGenerateScreenshotUploadUrl() {
  return useMutation({
    mutationFn: (filename: string) => uploadsApi.generateScreenshotUploadUrl(filename),
  });
}

export function useGenerateExportUrl() {
  return useMutation({
    mutationFn: (exportId: string) => uploadsApi.generateExportUrl(exportId),
  });
}

export function useGenerateExportDownloadUrl() {
  return useMutation({
    mutationFn: (exportId: string) => uploadsApi.generateExportDownloadUrl(exportId),
  });
}

export async function uploadFile(
  file: File,
  uploadUrl: string,
  onProgress?: (percent: number) => void,
): Promise<void> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.upload.addEventListener("progress", (e) => {
      if (e.lengthComputable && onProgress) {
        onProgress(Math.round((e.loaded / e.total) * 100));
      }
    });
    xhr.addEventListener("load", () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve();
      } else {
        reject(new Error(`Upload failed: ${xhr.status}`));
      }
    });
    xhr.addEventListener("error", () => reject(new Error("Upload failed")));
    xhr.open("PUT", uploadUrl);
    xhr.setRequestHeader("Content-Type", file.type);
    xhr.send(file);
  });
}
