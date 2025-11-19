'use client';

import React, { useState, useEffect } from 'react';
import { FileDropZone } from '../FileDropZone';
import { StrategicInput } from '../StrategicInput';
import { useGroundwork } from '../GroundworkProvider';
import { AssetsVisualsData, UploadedFile } from '@/lib/groundwork/types';

export function AssetsVisualsSection() {
  const { state, updateSectionData } = useGroundwork();
  const sectionData = state.sections['assets-visuals'].data as AssetsVisualsData | null;

  const [files, setFiles] = useState<UploadedFile[]>(sectionData?.files || []);

  useEffect(() => {
    const data: AssetsVisualsData = { files };
    updateSectionData('assets-visuals', data);
  }, [files, updateSectionData]);

  const handleFilesSelected = (selectedFiles: File[]) => {
    const newFiles: UploadedFile[] = selectedFiles.map((file) => ({
      id: `file-${Date.now()}-${Math.random()}`,
      name: file.name,
      type: file.type,
      size: file.size,
      url: URL.createObjectURL(file),
      ocrStatus: 'pending',
    }));

    setFiles([...files, ...newFiles]);

    // Simulate OCR processing
    setTimeout(() => {
      setFiles((prev) =>
        prev.map((f) =>
          newFiles.some((nf) => nf.id === f.id)
            ? { ...f, ocrStatus: 'processing' as const }
            : f
        )
      );

      setTimeout(() => {
        setFiles((prev) =>
          prev.map((f) =>
            newFiles.some((nf) => nf.id === f.id)
              ? { ...f, ocrStatus: 'completed' as const }
              : f
          )
        );
      }, 2000);
    }, 500);
  };

  const handleRemoveFile = (fileId: string) => {
    setFiles(files.filter((f) => f.id !== fileId));
  };

  const handleAttachFile = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    input.accept = '.pdf,.ppt,.pptx,.doc,.docx,.png,.jpg,.jpeg,.webp';
    input.onchange = (e) => {
      const target = e.target as HTMLInputElement;
      if (target.files) {
        handleFilesSelected(Array.from(target.files));
      }
    };
    input.click();
  };

  return (
    <div className="space-y-6">
      <FileDropZone
        onFilesSelected={handleFilesSelected}
        uploadedFiles={files}
        onRemoveFile={handleRemoveFile}
      />

      <div className="pt-4 border-t border-rf-cloud">
        <p className="text-sm text-rf-subtle mb-4">
          You can also attach files directly from the input box below when answering questions.
        </p>
        <StrategicInput
          value=""
          onChange={() => {}}
          placeholder="Type your notes about your assets here..."
          onAttachFile={handleAttachFile}
        />
      </div>
    </div>
  );
}

