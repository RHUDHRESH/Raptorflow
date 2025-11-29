import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, ArrowLeft, Plus, Users, Trash2, Check } from 'lucide-react';
import { LuxeHeading, LuxeCard, LuxeButton, LuxeInput, LuxeTextArea, LuxeBadge } from '../ui/PremiumUI';

const Act3Tribes = ({ positioning, strategy, onComplete }) => {
    const [icps, setIcps] = useState([
        {
            id: 'icp-1',
            name: 'New ICP',
            role: '',
            stage: '',
            wounds: '',
            triggers: '',
            objections: '',
            channels: '',
            outcome: ''
        }
    ]);
    const [selectedIcpId, setSelectedIcpId] = useState('icp-1');

    const selectedIcp = icps.find(icp => icp.id === selectedIcpId);

    const handleAddIcp = () => {
        if (icps.length >= 6) return;
        const newId = `icp-${Date.now()}`;
        setIcps(prev => [
            ...prev,
            {
                id: newId,
                name: 'New ICP',
                role: '',
                stage: '',
                wounds: '',
                triggers: '',
                objections: '',
                channels: '',
                outcome: ''
            }
        ]);
        setSelectedIcpId(newId);
    };

    const handleDeleteIcp = (id) => {
        setIcps(prev => prev.filter(icp => icp.id !== id));
        if (selectedIcpId === id) {
            setSelectedIcpId(icps[0]?.id || null);
        }
    };

    const updateIcp = (field, value) => {
        setIcps(prev => prev.map(icp =>
            icp.id === selectedIcpId ? { ...icp, [field]: value } : icp
        ));
    };

    const handleFinish = () => {
        if (icps.length > 0) {
            onComplete(icps);
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="w-full max-w-7xl mx-auto"
        >
            <div className="text-center mb-12">
                <LuxeBadge variant="outline" className="mb-4">Act III</LuxeBadge>
                <LuxeHeading level={2}>The Tribes</LuxeHeading>
                <p className="text-neutral-500 mt-2">Define your Ideal Customer Profiles (ICPs).</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                {/* Left: ICP List */}
                <div className="lg:col-span-4 space-y-6">
                    <div className="flex items-center justify-between">
                        <h3 className="text-xs font-bold text-neutral-400 uppercase tracking-widest">Your ICPs</h3>
                        <button
                            onClick={handleAddIcp}
                            disabled={icps.length >= 6}
                            className="text-xs font-bold text-neutral-900 uppercase tracking-widest hover:text-neutral-600 disabled:opacity-50 flex items-center gap-1"
                        >
                            <Plus className="w-3 h-3" /> Add ICP
                        </button>
                    </div>

                    <div className="space-y-3">
                        {icps.map(icp => (
                            <div
                                key={icp.id}
                                onClick={() => setSelectedIcpId(icp.id)}
                                className={`p-4 rounded-lg border cursor-pointer transition-all group relative ${selectedIcpId === icp.id
                                        ? 'bg-neutral-900 border-neutral-900 text-white shadow-lg'
                                        : 'bg-white border-neutral-200 hover:border-neutral-400 text-neutral-900'
                                    }`}
                            >
                                <div className="flex items-center gap-3">
                                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${selectedIcpId === icp.id ? 'bg-white/20' : 'bg-neutral-100'
                                        }`}>
                                        <Users className={`w-4 h-4 ${selectedIcpId === icp.id ? 'text-white' : 'text-neutral-500'}`} />
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <h4 className="font-bold text-sm truncate">{icp.name || 'New ICP'}</h4>
                                        <p className={`text-xs truncate ${selectedIcpId === icp.id ? 'text-neutral-400' : 'text-neutral-500'}`}>
                                            {icp.role || 'Define role...'}
                                        </p>
                                    </div>
                                    {icps.length > 1 && (
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                handleDeleteIcp(icp.id);
                                            }}
                                            className={`opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-red-500/20 transition-all ${selectedIcpId === icp.id ? 'text-white hover:text-red-200' : 'text-neutral-400 hover:text-red-600'
                                                }`}
                                        >
                                            <Trash2 className="w-3 h-3" />
                                        </button>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Right: ICP Form */}
                <div className="lg:col-span-8">
                    {selectedIcp ? (
                        <LuxeCard className="p-8 space-y-8">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div className="space-y-6">
                                    <h4 className="text-xs font-bold text-neutral-400 uppercase tracking-widest border-b border-neutral-100 pb-2">Who are they?</h4>
                                    <LuxeInput
                                        label="ICP Name"
                                        placeholder="e.g. Indie SaaS Founders"
                                        value={selectedIcp.name}
                                        onChange={(e) => updateIcp('name', e.target.value)}
                                    />
                                    <LuxeInput
                                        label="Role / Archetype"
                                        placeholder="e.g. Founder, CEO, CTO"
                                        value={selectedIcp.role}
                                        onChange={(e) => updateIcp('role', e.target.value)}
                                    />
                                    <LuxeInput
                                        label="Company Stage / Size"
                                        placeholder="e.g. $1-3M ARR, <10 employees"
                                        value={selectedIcp.stage}
                                        onChange={(e) => updateIcp('stage', e.target.value)}
                                    />
                                </div>
                                <div className="space-y-6">
                                    <h4 className="text-xs font-bold text-neutral-400 uppercase tracking-widest border-b border-neutral-100 pb-2">What hurts?</h4>
                                    <LuxeTextArea
                                        label="Key Wounds"
                                        placeholder="What keeps them up at night?"
                                        value={selectedIcp.wounds}
                                        onChange={(e) => updateIcp('wounds', e.target.value)}
                                        rows={4}
                                    />
                                    <LuxeTextArea
                                        label="Objections"
                                        placeholder="Why wouldn't they buy?"
                                        value={selectedIcp.objections}
                                        onChange={(e) => updateIcp('objections', e.target.value)}
                                        rows={3}
                                    />
                                </div>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-6 border-t border-neutral-100">
                                <div className="space-y-6">
                                    <h4 className="text-xs font-bold text-neutral-400 uppercase tracking-widest border-b border-neutral-100 pb-2">What moves them?</h4>
                                    <LuxeTextArea
                                        label="Triggers"
                                        placeholder="What events trigger a purchase?"
                                        value={selectedIcp.triggers}
                                        onChange={(e) => updateIcp('triggers', e.target.value)}
                                        rows={3}
                                    />
                                    <LuxeInput
                                        label="Desired Outcome"
                                        placeholder="What does success look like?"
                                        value={selectedIcp.outcome}
                                        onChange={(e) => updateIcp('outcome', e.target.value)}
                                    />
                                </div>
                                <div className="space-y-6">
                                    <h4 className="text-xs font-bold text-neutral-400 uppercase tracking-widest border-b border-neutral-100 pb-2">Where are they?</h4>
                                    <LuxeInput
                                        label="Primary Channels"
                                        placeholder="LinkedIn, Twitter, SEO..."
                                        value={selectedIcp.channels}
                                        onChange={(e) => updateIcp('channels', e.target.value)}
                                    />
                                </div>
                            </div>
                        </LuxeCard>
                    ) : (
                        <div className="h-full flex items-center justify-center text-neutral-400">
                            Select an ICP to edit
                        </div>
                    )}

                    <div className="pt-8 flex justify-end">
                        <LuxeButton
                            onClick={handleFinish}
                            disabled={icps.length === 0}
                            size="lg"
                            className="w-full md:w-auto"
                        >
                            Save ICPs & Finish <Check className="ml-2 w-4 h-4" />
                        </LuxeButton>
                    </div>
                </div>
            </div>
        </motion.div>
    );
};

export default Act3Tribes;
