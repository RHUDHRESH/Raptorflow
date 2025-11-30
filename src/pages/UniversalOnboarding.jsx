import React, { useState } from 'react';
import { PageHeader } from '../components/ui/PremiumUI';
import { OmnivoresUploadZone } from '../components/intelligence/OmnivoresUploadZone';
import { useNavigate } from 'react-router-dom';

const UniversalOnboarding = () => {
    const navigate = useNavigate();
    const [uploadResults, setUploadResults] = useState([]);

    const handleUploadComplete = (data) => {
        setUploadResults(prev => [...prev, data]);
        console.log("Intelligence Extracted:", data);
    };

    return (
        <div className="min-h-screen bg-white">
            <div className="max-w-5xl mx-auto px-6 py-12">
                <PageHeader 
                    title="Universal Intelligence Extraction" 
                    subtitle="We need to understand you better than you understand yourself. Drop anything to start."
                    backUrl="/dashboard"
                />
                
                <div className="mt-12">
                    <OmnivoresUploadZone onUploadComplete={handleUploadComplete} />
                </div>

                {/* Visualization of Extracted Intelligence (Placeholder for next steps) */}
                {uploadResults.length > 0 && (
                    <div className="mt-12 border-t border-neutral-200 pt-12">
                        <h3 className="text-2xl font-display font-medium mb-6">Extracted Intelligence</h3>
                        <div className="grid gap-6">
                            {uploadResults.map((res, i) => (
                                <div key={i} className="bg-neutral-50 p-6 rounded-lg border border-neutral-200">
                                    <pre className="text-xs overflow-auto max-h-60">
                                        {JSON.stringify(res, null, 2)}
                                    </pre>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default UniversalOnboarding;
