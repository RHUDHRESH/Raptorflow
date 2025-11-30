import React, { useState, useCallback } from 'react';
import { LuxeCard, LuxeButton, LuxeHeading } from '../ui/PremiumUI';
import { Upload, Link as LinkIcon, FileText, Loader2 } from 'lucide-react';

export const OmnivoresUploadZone = ({ onUploadComplete }) => {
    const [dragActive, setDragActive] = useState(false);
    const [files, setFiles] = useState([]);
    const [urlInput, setUrlInput] = useState('');
    const [isUploading, setIsUploading] = useState(false);

    const handleDrag = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    }, []);

    const handleDrop = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFiles(e.dataTransfer.files);
        }
    }, []);

    const handleChange = (e) => {
        e.preventDefault();
        if (e.target.files && e.target.files[0]) {
            handleFiles(e.target.files);
        }
    };

    const handleFiles = async (fileList) => {
        const newFiles = Array.from(fileList).map(file => ({
            file,
            name: file.name,
            type: file.type,
            status: 'pending',
            progress: 0,
            message: 'Waiting...'
        }));
        setFiles(prev => [...prev, ...newFiles]);
        
        // Process immediately
        await processFiles(newFiles);
    };

    const processFiles = async (newFiles) => {
        setIsUploading(true);
        for (const fileObj of newFiles) {
            updateFileStatus(fileObj.name, { status: 'uploading', message: 'Uploading...' });
            
            const formData = new FormData();
            formData.append('file', fileObj.file);
            
            try {
                const token = localStorage.getItem('token');
                const response = await fetch('http://localhost:8000/api/v1/intelligence/upload', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    },
                    body: formData
                });
                
                if (response.ok) {
                    const data = await response.json();
                    updateFileStatus(fileObj.name, { status: 'queued', message: 'Queued for processing...' });
                    // Start polling
                    pollStatus(data.task_id, fileObj.name);
                } else {
                    updateFileStatus(fileObj.name, { status: 'error', message: 'Upload failed' });
                }
            } catch (error) {
                console.error("Upload error:", error);
                updateFileStatus(fileObj.name, { status: 'error', message: 'Network error' });
            }
        }
        setIsUploading(false);
    };

    const updateFileStatus = (fileName, updates) => {
        setFiles(prev => prev.map(f => 
            f.name === fileName ? { ...f, ...updates } : f
        ));
    };

    const pollStatus = (taskId, fileName) => {
        const interval = setInterval(async () => {
            try {
                const token = localStorage.getItem('token');
                const res = await fetch(`http://localhost:8000/api/v1/intelligence/task/${taskId}`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (res.ok) {
                    const data = await res.json();
                    
                    // Map backend status to frontend state
                    let status = data.status;
                    if (status === 'processing') status = 'processing';
                    if (status === 'completed') status = 'complete';
                    if (status === 'failed') status = 'error';

                    updateFileStatus(fileName, { 
                        status, 
                        progress: data.progress || 0,
                        message: data.message || status 
                    });
                    
                    if (status === 'complete' || status === 'error') {
                        clearInterval(interval);
                        if (status === 'complete' && onUploadComplete) {
                            onUploadComplete(data.result);
                        }
                    }
                }
            } catch (e) {
                console.error("Polling error", e);
            }
        }, 2000);
    };

    const handleUrlSubmit = async (e) => {
        e.preventDefault();
        if (!urlInput) return;
        
        const urlFile = { name: urlInput, type: 'url', status: 'uploading', progress: 0, message: 'Submitting URL...' };
        setFiles(prev => [...prev, urlFile]);
        setUrlInput('');
        
        try {
            const token = localStorage.getItem('token');
            const response = await fetch('http://localhost:8000/api/v1/intelligence/analyze-url', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ url: urlFile.name })
            });
            
            if (response.ok) {
                const data = await response.json();
                updateFileStatus(urlFile.name, { status: 'queued', message: 'Queued...' });
                pollStatus(data.task_id, urlFile.name);
            } else {
                updateFileStatus(urlFile.name, { status: 'error', message: 'Submission failed' });
            }
        } catch (error) {
            updateFileStatus(urlFile.name, { status: 'error', message: 'Network error' });
        }
    };

    return (
        <div className="w-full max-w-4xl mx-auto space-y-6">
            <LuxeCard className={`border-2 border-dashed transition-colors duration-200 ${
                dragActive ? 'border-neutral-900 bg-neutral-50' : 'border-neutral-200'
            }`}>
                <div 
                    className="flex flex-col items-center justify-center p-12 text-center"
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                >
                    <div className="p-4 bg-neutral-100 rounded-full mb-4">
                        <Upload className="w-8 h-8 text-neutral-600" />
                    </div>
                    <LuxeHeading level={3} className="mb-2">
                        Drop Anything. We'll Extract Everything.
                    </LuxeHeading>
                    <p className="text-neutral-500 mb-8 max-w-md">
                        Business plan, pitch deck, website URL, competitor links, 
                        photos, videos... literally anything.
                    </p>
                    
                    <div className="flex flex-col sm:flex-row gap-4 w-full max-w-md">
                        <div className="relative flex-1">
                            <input
                                type="file"
                                className="hidden"
                                id="file-upload"
                                multiple
                                onChange={handleChange}
                            />
                            <label htmlFor="file-upload">
                                <LuxeButton variant="primary" className="w-full" as="span">
                                    Upload Files
                                </LuxeButton>
                            </label>
                        </div>
                    </div>
                    
                    <div className="mt-6 w-full max-w-md">
                        <div className="relative">
                            <div className="absolute inset-0 flex items-center">
                                <span className="w-full border-t border-neutral-200" />
                            </div>
                            <div className="relative flex justify-center text-xs uppercase">
                                <span className="bg-white px-2 text-neutral-500">Or paste a URL</span>
                            </div>
                        </div>
                        <form onSubmit={handleUrlSubmit} className="mt-4 flex gap-2">
                            <div className="relative flex-1">
                                <LinkIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                                <input
                                    type="url"
                                    value={urlInput}
                                    onChange={(e) => setUrlInput(e.target.value)}
                                    placeholder="https://example.com"
                                    className="w-full pl-9 pr-4 py-2 border border-neutral-200 rounded-md focus:outline-none focus:border-neutral-900"
                                />
                            </div>
                            <LuxeButton type="submit" variant="secondary" disabled={!urlInput}>
                                Analyze
                            </LuxeButton>
                        </form>
                    </div>
                </div>
            </LuxeCard>

            {/* Processing Status */}
            {files.length > 0 && (
                <div className="space-y-3">
                    <LuxeHeading level={5}>Processing Queue</LuxeHeading>
                    {files.map((file, idx) => (
                        <div key={idx} className="flex items-center justify-between p-4 bg-white border border-neutral-200 rounded-lg shadow-sm">
                            <div className="flex items-center gap-3">
                                {file.type === 'url' ? (
                                    <div className="p-2 bg-blue-50 rounded text-blue-600">
                                        <LinkIcon className="w-4 h-4" />
                                    </div>
                                ) : (
                                    <div className="p-2 bg-orange-50 rounded text-orange-600">
                                        <FileText className="w-4 h-4" />
                                    </div>
                                )}
                                <div>
                                    <p className="font-medium text-sm text-neutral-900">{file.name}</p>
                                    <div className="flex items-center gap-2">
                                        <p className="text-xs text-neutral-500 capitalize">{file.message}</p>
                                        {file.status === 'processing' && (
                                            <div className="w-24 h-1.5 bg-neutral-100 rounded-full overflow-hidden">
                                                <div 
                                                    className="h-full bg-neutral-900 transition-all duration-500"
                                                    style={{ width: `${file.progress}%` }}
                                                />
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                            <div>
                                {(file.status === 'uploading' || file.status === 'queued' || file.status === 'processing') && (
                                    <Loader2 className="w-5 h-5 animate-spin text-neutral-400" />
                                )}
                                {file.status === 'complete' && <span className="text-xs font-medium text-green-600 bg-green-50 px-2 py-1 rounded">Extracted</span>}
                                {file.status === 'error' && <span className="text-xs font-medium text-red-600 bg-red-50 px-2 py-1 rounded">Failed</span>}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};
