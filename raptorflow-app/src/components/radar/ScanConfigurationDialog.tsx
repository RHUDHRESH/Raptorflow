'use client';

import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { RadarMode } from './types';
import { Zap, FileText, Loader2, ChevronDown, Settings2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';

interface ScanConfigurationDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  initialMode: RadarMode;
  onStartScan: (config: ScanConfig) => void;
}

export interface ScanConfig {
  mode: RadarMode;
  timeWindow: string;
  targetCohorts: string[];
  keywords: string;
  formats: string[];
  sources: string[];
}

const COHORTS = [
  { id: 'founders', label: 'Early-stage Founders' },
  { id: 'marketing', label: 'Marketing Managers' },
  { id: 'tech', label: 'Tech Enthusiasts' },
  { id: 'agency', label: 'Agency Owners' },
];

const FORMATS = [
  { id: 'linkedin', label: 'LinkedIn Posts' },
  { id: 'twitter', label: 'X / Twitter Threads' },
  { id: 'email', label: 'Cold Emails' },
  { id: 'blog', label: 'Short Blog Posts' },
];

const SOURCES = [
  { id: 'linkedin', label: 'LinkedIn' },
  { id: 'x', label: 'X / Twitter' },
  { id: 'reddit', label: 'Reddit' },
  { id: 'google', label: 'Global News' },
];

export function ScanConfigurationDialog({
  open,
  onOpenChange,
  initialMode,
  onStartScan,
}: ScanConfigurationDialogProps) {
  const [mode, setMode] = useState<RadarMode>(initialMode);
  const [timeWindow, setTimeWindow] = useState('7d');
  const [selectedCohorts, setSelectedCohorts] = useState<string[]>([
    'founders',
  ]);
  const [selectedFormats, setSelectedFormats] = useState<string[]>([
    'linkedin',
  ]);
  const [selectedSources, setSelectedSources] = useState<string[]>([
    'linkedin',
    'x',
  ]);
  const [keywords, setKeywords] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const toggleCohort = (id: string) => {
    setSelectedCohorts((prev) =>
      prev.includes(id) ? prev.filter((c) => c !== id) : [...prev, id]
    );
  };

  const toggleFormat = (id: string) => {
    setSelectedFormats((prev) =>
      prev.includes(id) ? prev.filter((f) => f !== id) : [...prev, id]
    );
  };

  const toggleSource = (id: string) => {
    setSelectedSources((prev) =>
      prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id]
    );
  };

  const handleStart = () => {
    setIsLoading(true);
    setTimeout(() => {
      onStartScan({
        mode,
        timeWindow,
        targetCohorts: selectedCohorts,
        keywords,
        formats: selectedFormats,
        sources: selectedSources,
      });
      setIsLoading(false);
      onOpenChange(false);
    }, 800);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[550px] p-0 gap-0 overflow-hidden bg-card">
        <DialogHeader className="p-6 border-b border-border/40 bg-secondary/10">
          <DialogTitle className="font-display text-2xl font-semibold tracking-tight">
            {mode === 'recon' ? 'Recon Scan' : 'Compile Dossier'}
          </DialogTitle>
          <p className="text-sm text-muted-foreground mt-1">
            Start a new search to find fresh signals or compile a deep dossier.
          </p>
        </DialogHeader>

        <div className="p-6 space-y-8 max-h-[70vh] overflow-y-auto">
          {/* Mode Selection - The Primary Choice */}
          <div className="space-y-3">
            <Label className="text-xs uppercase tracking-wider text-muted-foreground font-semibold">
              Scanning Mode
            </Label>
            <Tabs
              value={mode}
              onValueChange={(v) => setMode(v as RadarMode)}
              className="w-full"
            >
              <TabsList className="grid w-full grid-cols-2 h-14 bg-secondary/50 p-1 rounded-xl">
                <TabsTrigger
                  value="recon"
                  className="gap-2 rounded-lg data-[state=active]:bg-background data-[state=active]:shadow-md transition-all"
                >
                  <Zap className="h-5 w-5" />
                  <div className="text-left">
                    <div className="text-sm font-semibold">Recon</div>
                    <div className="text-[10px] text-muted-foreground leading-tight">
                      Fast Signal Pulse
                    </div>
                  </div>
                </TabsTrigger>
                <TabsTrigger
                  value="dossier"
                  className="gap-2 rounded-lg data-[state=active]:bg-background data-[state=active]:shadow-md transition-all"
                >
                  <FileText className="h-5 w-5" />
                  <div className="text-left">
                    <div className="text-sm font-semibold">Dossier</div>
                    <div className="text-[10px] text-muted-foreground leading-tight">
                      Deep Synthesis
                    </div>
                  </div>
                </TabsTrigger>
              </TabsList>
            </Tabs>
          </div>

          {/* Simple Message */}
          <p className="text-xs text-center text-muted-foreground">
            Ready to scan for{' '}
            <span className="text-foreground font-medium">
              all active cohorts
            </span>{' '}
            using standard parameters.
          </p>

          {/* Advanced Section */}
          <Accordion
            type="single"
            collapsible
            className="w-full border rounded-xl overflow-hidden border-border/60 shadow-sm"
          >
            <AccordionItem value="advanced" className="border-none">
              <AccordionTrigger className="px-5 py-4 hover:bg-secondary/20 transition-all hover:no-underline">
                <div className="flex items-center gap-3">
                  <div className="h-8 w-8 rounded-lg bg-secondary/50 flex items-center justify-center">
                    <Settings2 className="h-4 w-4 text-foreground" />
                  </div>
                  <div className="text-left">
                    <div className="text-sm font-semibold">
                      Advanced Configuration
                    </div>
                    <div className="text-xs text-muted-foreground">
                      Tweak sources, cohorts & window
                    </div>
                  </div>
                </div>
              </AccordionTrigger>
              <AccordionContent className="p-5 pt-2 space-y-8">
                {/* Lookback & Keywords */}
                <div className="grid grid-cols-2 gap-6">
                  <div className="space-y-3">
                    <Label className="text-xs uppercase tracking-wider text-muted-foreground font-semibold">
                      Lookback
                    </Label>
                    <Select value={timeWindow} onValueChange={setTimeWindow}>
                      <SelectTrigger className="h-11 rounded-xl border-border/60">
                        <SelectValue placeholder="Select window" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="24h">Last 24 Hours</SelectItem>
                        <SelectItem value="3d">Last 3 Days</SelectItem>
                        <SelectItem value="7d">Last 7 Days</SelectItem>
                        <SelectItem value="30d">Last 30 Days</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-3">
                    <Label className="text-xs uppercase tracking-wider text-muted-foreground font-semibold">
                      Keywords
                    </Label>
                    <Input
                      placeholder="Optional focus..."
                      value={keywords}
                      onChange={(e) => setKeywords(e.target.value)}
                      className="h-11 rounded-xl border-border/60"
                    />
                  </div>
                </div>

                {/* Multi-Cohort Selection */}
                <div className="space-y-4">
                  <Label className="text-xs uppercase tracking-wider text-muted-foreground font-semibold">
                    Target Cohorts
                  </Label>
                  <div className="grid grid-cols-2 gap-3">
                    {COHORTS.map((cohort) => (
                      <div
                        key={cohort.id}
                        className={cn(
                          'flex items-center gap-3 p-3 rounded-lg border transition-all cursor-pointer',
                          selectedCohorts.includes(cohort.id)
                            ? 'bg-primary/5 border-primary/40 ring-1 ring-primary/20'
                            : 'bg-transparent border-transparent hover:bg-secondary/40'
                        )}
                        onClick={() => toggleCohort(cohort.id)}
                      >
                        <Checkbox
                          id={cohort.id}
                          checked={selectedCohorts.includes(cohort.id)}
                          onCheckedChange={() => toggleCohort(cohort.id)}
                        />
                        <label
                          htmlFor={cohort.id}
                          className="text-sm cursor-pointer leading-none font-medium"
                        >
                          {cohort.label}
                        </label>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Sources */}
                <div className="space-y-4">
                  <Label className="text-xs uppercase tracking-wider text-muted-foreground font-semibold">
                    Intelligence Sources
                  </Label>
                  <div className="grid grid-cols-2 gap-3">
                    {SOURCES.map((source) => (
                      <div
                        key={source.id}
                        className={cn(
                          'flex items-center gap-3 p-3 rounded-lg border transition-all cursor-pointer',
                          selectedSources.includes(source.id)
                            ? 'bg-primary/5 border-primary/40 ring-1 ring-primary/20'
                            : 'bg-transparent border-transparent hover:bg-secondary/40'
                        )}
                        onClick={() => toggleSource(source.id)}
                      >
                        <Checkbox
                          id={source.id}
                          checked={selectedSources.includes(source.id)}
                          onCheckedChange={() => toggleSource(source.id)}
                        />
                        <label
                          htmlFor={source.id}
                          className="text-sm cursor-pointer leading-none font-medium"
                        >
                          {source.label}
                        </label>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Content Formats */}
                <div className="space-y-4">
                  <Label className="text-xs uppercase tracking-wider text-muted-foreground font-semibold">
                    Output Formats
                  </Label>
                  <div className="grid grid-cols-2 gap-3">
                    {FORMATS.map((format) => (
                      <div
                        key={format.id}
                        className={cn(
                          'flex items-center gap-3 p-3 rounded-lg border transition-all cursor-pointer',
                          selectedFormats.includes(format.id)
                            ? 'bg-primary/5 border-primary/40 ring-1 ring-primary/20'
                            : 'bg-transparent border-transparent hover:bg-secondary/40'
                        )}
                        onClick={() => toggleFormat(format.id)}
                      >
                        <Checkbox
                          id={format.id}
                          checked={selectedFormats.includes(format.id)}
                          onCheckedChange={() => toggleFormat(format.id)}
                        />
                        <label
                          htmlFor={format.id}
                          className="text-sm cursor-pointer leading-none font-medium"
                        >
                          {format.label}
                        </label>
                      </div>
                    ))}
                  </div>
                </div>
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </div>

        <DialogFooter className="p-6 pt-2 bg-secondary/10 border-t border-border/40">
          <Button
            variant="ghost"
            onClick={() => onOpenChange(false)}
            className="rounded-xl"
          >
            Cancel
          </Button>
          <Button
            onClick={handleStart}
            disabled={isLoading || selectedCohorts.length === 0}
            className="gap-2 px-10 h-12 rounded-xl shadow-lg transition-all active:scale-95 text-base"
          >
            {isLoading ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <Zap className="h-5 w-5" />
            )}
            {mode === 'recon' ? 'Execute Recon' : 'Complete Compilation'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
