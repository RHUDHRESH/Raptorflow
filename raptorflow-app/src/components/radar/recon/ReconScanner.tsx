'use client';

import React, { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import { useFoundation } from '@/context/FoundationProvider';
import { Search, Link as LinkIcon, Sparkles } from 'lucide-react';

interface ReconScannerProps {
    onScan: (icpId: string, urls: string[]) => void;
    isLoading: boolean;
}

export function ReconScanner({ onScan, isLoading }: ReconScannerProps) {
    const { getIcps } = useFoundation();
    const icps = getIcps();
    const [selectedIcp, setSelectedIcp] = useState<string>('');
    const [urls, setUrls] = useState<string>('');

    const handleScan = () => {
        const urlList = urls
            .split('\n')
            .map((u) => u.trim())
            .filter((u) => u.length > 0);
        onScan(selectedIcp || 'default', urlList);
    };

    return (
        <Card className="border-[#C0C1BE] bg-[#F8F9F7]/50 shadow-none">
            <CardContent className="p-6 space-y-6">
                <div className="grid grid-cols-2 gap-6">
                    <div className="space-y-2">
                        <label className="text-xs font-semibold text-[#5B5F61] uppercase tracking-wider">
                            Target ICP
                        </label>
                        <Select value={selectedIcp} onValueChange={setSelectedIcp}>
                            <SelectTrigger className="bg-white border-[#C0C1BE] h-11 rounded-xl">
                                <SelectValue placeholder="Select target cohort..." />
                            </SelectTrigger>
                            <SelectContent>
                                {icps.map((icp) => (
                                    <SelectItem key={icp.icp_id} value={icp.icp_id}>
                                        {icp.name}
                                    </SelectItem>
                                ))}
                                {icps.length === 0 && (
                                    <SelectItem value="default" disabled>
                                        No ICPs found in foundation
                                    </SelectItem>
                                )}
                            </SelectContent>
                        </Select>
                        <p className="text-[11px] text-[#9D9F9F]">
                            Radar will orient signals based on this cohort's pains and JTBD.
                        </p>
                    </div>

                    <div className="space-y-2">
                        <label className="text-xs font-semibold text-[#5B5F61] uppercase tracking-wider">
                            Source URLs (Optional)
                        </label>
                        <div className="relative">
                            <Textarea
                                placeholder="Paste competitor URLs, LinkedIn profiles, or blog links..."
                                className="bg-white border-[#C0C1BE] min-h-[44px] py-3 rounded-xl resize-none"
                                value={urls}
                                onChange={(e) => setUrls(e.target.value)}
                            />
                        </div>
                        <p className="text-[11px] text-[#9D9F9F]">
                            One URL per line. Leave empty to scan global market trends.
                        </p>
                    </div>
                </div>

                <div className="flex justify-end pt-2">
                    <Button
                        onClick={handleScan}
                        disabled={isLoading || (!selectedIcp && !urls.trim())}
                        className="bg-[#1A1D1E] hover:bg-black text-white h-12 px-8 rounded-2xl shadow-lg transition-all"
                    >
                        {isLoading ? (
                            <>
                                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
                                Scanning Market...
                            </>
                        ) : (
                            <>
                                <Search className="w-4 h-4 mr-2" />
                                Initialize Recon Scan
                            </>
                        )}
                    </Button>
                </div>
            </CardContent>
        </Card>
    );
}
