"use client"

import React, { useState, useCallback } from "react"
import { Upload, FileText, X, CheckCircle2, Loader2, Sparkles } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import { cn } from "@/lib/utils"
import { toast } from "sonner"

export function SkillUploadZone() {
    const [isDragging, setIsDragging] = useState(false)
    const [files, setFiles] = useState<{ id: string, name: string, status: 'uploading' | 'processing' | 'done', progress: number }[]>([])

    const onDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault()
        setIsDragging(true)
    }, [])

    const onDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault()
        setIsDragging(false)
    }, [])

    const onDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault()
        setIsDragging(false)
        const droppedFiles = Array.from(e.dataTransfer.files)
        handleFiles(droppedFiles)
    }, [])

    const handleFiles = (newFiles: File[]) => {
        const validFiles = newFiles.filter(f => f.type === 'application/pdf' || f.name.endsWith('.docx') || f.name.endsWith('.txt'))

        if (validFiles.length < newFiles.length) {
            toast.error("Only PDF, DOCX, and TXT files are accepted.")
        }

        const fileObjects = validFiles.map(f => ({
            id: Math.random().toString(36).substr(2, 9),
            name: f.name,
            status: 'uploading' as const,
            progress: 0
        }))

        setFiles(prev => [...fileObjects, ...prev])

        // Simulate upload and processing
        fileObjects.forEach(fileObj => {
            simulateWorkflow(fileObj.id)
        })
    }

    const simulateWorkflow = (id: string) => {
        // Upload simulation
        setTimeout(() => {
            setFiles(prev => prev.map(f => f.id === id ? { ...f, progress: 100, status: 'processing' } : f))

            // Processing simulation (Librarian Agent)
            setTimeout(() => {
                setFiles(prev => prev.map(f => f.id === id ? { ...f, status: 'done' } : f))
                toast.success("Knowledge ingested. Experts are training.")
            }, 3000)
        }, 1500)
    }

    const removeFile = (id: string) => {
        setFiles(prev => prev.filter(f => f.id !== id))
    }

    return (
        <div className="space-y-6">
            <header>
                <h3 className="text-lg font-serif italic text-ink">Skill Ingestion</h3>
                <p className="text-xs text-secondary-text mt-1">Upload strategy docs, brand guides, or industry reports to train the Council.</p>
            </header>

            <div
                onDragOver={onDragOver}
                onDragLeave={onDragLeave}
                onDrop={onDrop}
                className={cn(
                    "relative min-h-[200px] rounded-3xl border-2 border-dashed transition-all duration-300 flex flex-col items-center justify-center p-8 text-center",
                    isDragging ? "border-accent bg-accent/5" : "border-borders/50 bg-surface/30 hover:border-borders hover:bg-surface/50"
                )}
            >
                <div className="p-4 rounded-full bg-canvas border border-borders/30 mb-4 shadow-sm">
                    <Upload className={cn("h-6 w-6 transition-colors", isDragging ? "text-accent" : "text-muted-fill")} />
                </div>
                <div className="space-y-1">
                    <p className="text-sm font-medium text-ink">Drag & Drop knowledge artifacts</p>
                    <p className="text-[11px] text-secondary-text">PDF, DOCX, or TXT (Max 20MB)</p>
                </div>

                <input
                    type="file"
                    multiple
                    className="absolute inset-0 opacity-0 cursor-pointer"
                    onChange={(e) => e.target.files && handleFiles(Array.from(e.target.files))}
                    accept=".pdf,.docx,.txt"
                />
            </div>

            <AnimatePresence>
                {files.length > 0 && (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="space-y-3"
                    >
                        <h4 className="text-[10px] font-bold uppercase tracking-widest text-muted-fill">Active Training</h4>
                        {files.map((file) => (
                            <motion.div
                                key={file.id}
                                layout
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, scale: 0.95 }}
                                className="flex items-center gap-4 p-4 rounded-2xl bg-surface border border-borders/50 shadow-sm"
                            >
                                <div className="p-2 rounded-lg bg-canvas border border-borders/30 text-accent">
                                    <FileText className="h-4 w-4" />
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="flex justify-between items-center mb-1">
                                        <p className="text-sm font-medium text-ink truncate">{file.name}</p>
                                        <span className="text-[10px] font-mono text-secondary-text uppercase">
                                            {file.status}
                                        </span>
                                    </div>
                                    <div className="h-1 bg-borders/20 rounded-full overflow-hidden">
                                        <motion.div
                                            className={cn(
                                                "h-full rounded-full transition-all duration-500",
                                                file.status === 'done' ? "bg-green-500" : "bg-accent"
                                            )}
                                            initial={{ width: 0 }}
                                            animate={{ width: `${file.status === 'done' ? 100 : file.progress || 50}%` }}
                                        />
                                    </div>
                                </div>
                                <div className="flex items-center gap-2">
                                    {file.status === 'processing' && <Loader2 className="h-4 w-4 text-accent animate-spin" />}
                                    {file.status === 'done' && <CheckCircle2 className="h-4 w-4 text-green-500" />}
                                    <button
                                        onClick={() => removeFile(file.id)}
                                        className="p-1 hover:bg-red-50 hover:text-red-500 rounded-md transition-colors text-secondary-text"
                                    >
                                        <X className="h-4 w-4" />
                                    </button>
                                </div>
                            </motion.div>
                        ))}
                    </motion.div>
                )}
            </AnimatePresence>

            {files.some(f => f.status === 'done') && (
                <div className="p-4 rounded-2xl bg-accent/5 border border-accent/20 flex gap-3 items-center">
                    <Sparkles className="h-4 w-4 text-accent" />
                    <p className="text-[11px] text-primary-text font-medium italic">
                        The Librarian is extracting heuristics from your documents to update Expert DNA.
                    </p>
                </div>
            )}
        </div>
    )
}
