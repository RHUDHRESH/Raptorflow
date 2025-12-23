import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Copy, Mail, Download, Share2, Check } from 'lucide-react';

interface ShareExportModalProps {
    isOpen: boolean;
    onClose: () => void;
    data: any; // The ICP data
}

export const ShareExportModal: React.FC<ShareExportModalProps> = ({ isOpen, onClose, data }) => {
    const [copied, setCopied] = useState(false);

    const handleCopy = () => {
        navigator.clipboard.writeText(JSON.stringify(data, null, 2));
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <motion.div
                        className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                    />

                    {/* Modal */}
                    <motion.div
                        className="fixed inset-0 flex items-center justify-center z-50 pointer-events-none"
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                    >
                        <div className="bg-[#F3F4EE] w-full max-w-md rounded-2xl shadow-2xl border border-[#C0C1BE] pointer-events-auto overflow-hidden">
                            {/* Header */}
                            <div className="bg-[#2D3538] text-[#F3F4EE] px-6 py-4 flex items-center justify-between">
                                <h3 className="text-lg font-serif font-medium flex items-center gap-2">
                                    <Share2 className="w-5 h-5" />
                                    Share & Export
                                </h3>
                                <button onClick={onClose} className="hover:bg-white/10 p-1 rounded-full transition-colors">
                                    <X className="w-5 h-5" />
                                </button>
                            </div>

                            {/* Content */}
                            <div className="p-6 space-y-6">
                                <p className="text-[#5B5F61] text-sm">
                                    Your ICP is ready. Share it with your team or export it to start your campaigns.
                                </p>

                                <div className="grid grid-cols-2 gap-4">
                                    <button
                                        onClick={handleCopy}
                                        className="flex flex-col items-center justify-center p-4 bg-white border border-[#C0C1BE] rounded-xl hover:border-[#2D3538] hover:shadow-md transition-all group"
                                    >
                                        <div className="w-10 h-10 bg-[#F3F4EE] rounded-full flex items-center justify-center mb-2 group-hover:bg-[#E5E7E1] transition-colors">
                                            {copied ? <Check className="w-5 h-5 text-green-600" /> : <Copy className="w-5 h-5 text-[#2D3538]" />}
                                        </div>
                                        <span className="text-sm font-medium text-[#2D3538]">{copied ? 'Copied!' : 'Copy JSON'}</span>
                                    </button>

                                    <button className="flex flex-col items-center justify-center p-4 bg-white border border-[#C0C1BE] rounded-xl hover:border-[#2D3538] hover:shadow-md transition-all group opacity-50 cursor-not-allowed">
                                        <div className="w-10 h-10 bg-[#F3F4EE] rounded-full flex items-center justify-center mb-2">
                                            <Download className="w-5 h-5 text-[#2D3538]" />
                                        </div>
                                        <span className="text-sm font-medium text-[#2D3538]">Download PDF</span>
                                    </button>

                                    <button className="flex flex-col items-center justify-center p-4 bg-white border border-[#C0C1BE] rounded-xl hover:border-[#2D3538] hover:shadow-md transition-all group opacity-50 cursor-not-allowed">
                                        <div className="w-10 h-10 bg-[#F3F4EE] rounded-full flex items-center justify-center mb-2">
                                            <Mail className="w-5 h-5 text-[#2D3538]" />
                                        </div>
                                        <span className="text-sm font-medium text-[#2D3538]">Email Team</span>
                                    </button>

                                    <button className="flex flex-col items-center justify-center p-4 bg-white border border-[#C0C1BE] rounded-xl hover:border-[#2D3538] hover:shadow-md transition-all group opacity-50 cursor-not-allowed">
                                        <div className="w-10 h-10 bg-[#F3F4EE] rounded-full flex items-center justify-center mb-2">
                                            <Share2 className="w-5 h-5 text-[#2D3538]" />
                                        </div>
                                        <span className="text-sm font-medium text-[#2D3538]">Public Link</span>
                                    </button>
                                </div>

                                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 text-xs text-yellow-800 flex gap-2">
                                    <span className="font-bold">NOTE:</span> Export features are coming in the next update. Copy JSON is active.
                                </div>
                            </div>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
};
