import React, { useEffect, useRef, useState } from 'react';
import { Question } from '@/lib/questionFlowData';
import styles from './QuestionFlow.module.css';
import { Check, FileText, X } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { cn } from '@/lib/utils';

interface QuestionInputProps {
    question: Question;
    value: any;
    onChange: (value: any) => void;
    onEnter: () => void;
}

export function QuestionInput({ question, value, onChange, onEnter }: QuestionInputProps) {
    const inputRef = useRef<HTMLInputElement | HTMLTextAreaElement>(null);
    const [focusedCardIndex, setFocusedCardIndex] = useState(-1);
    const [isDragging, setIsDragging] = useState(false);

    useEffect(() => {
        setFocusedCardIndex(-1); // Reset
        setTimeout(() => inputRef.current?.focus(), 150);
    }, [question.id]);

    const handleGridKeyDown = (e: React.KeyboardEvent, options: any[]) => {
        if (!options) return;
        let nextIndex = focusedCardIndex;

        // Simple linear navigation for now
        if (e.key === 'ArrowDown' || e.key === 'ArrowRight') {
            nextIndex = nextIndex < options.length - 1 ? nextIndex + 1 : 0;
            e.preventDefault();
        } else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') {
            nextIndex = nextIndex > 0 ? nextIndex - 1 : options.length - 1;
            e.preventDefault();
        } else if (e.key === 'Enter' || e.key === ' ') {
            if (focusedCardIndex >= 0) {
                e.preventDefault();
                const option = options[focusedCardIndex];
                if (option) {
                    if (question.type === 'multi-select') {
                        const vals = Array.isArray(value) ? value : [];
                        const isSel = vals.includes(option.value);
                        const newVals = isSel ? vals.filter((v: string) => v !== option.value) : [...vals, option.value];
                        onChange(newVals);
                    } else {
                        onChange(option.value);
                        setTimeout(onEnter, 300);
                    }
                }
            }
        }
        setFocusedCardIndex(nextIndex);
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey && question.type !== 'textarea') {
            e.preventDefault();
            onEnter();
        }
    };

    switch (question.type) {
        case 'text':
            return (
                <Input
                    ref={inputRef as any}
                    className="h-14 text-lg bg-background border-2 focus-visible:ring-0 focus-visible:border-primary shadow-sm"
                    value={value}
                    onChange={e => onChange(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder={question.placeholder}
                />
            );
        case 'text-large':
            return (
                <Input
                    ref={inputRef as any}
                    className="h-20 text-2xl font-serif bg-background border-2 focus-visible:ring-2 focus-visible:border-primary px-8 shadow-sm"
                    value={value}
                    onChange={e => onChange(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder={question.placeholder}
                />
            );
        case 'textarea':
            return (
                <div className="relative">
                    <Textarea
                        ref={inputRef as any}
                        className="min-h-[180px] text-lg p-6 resize-none bg-background border-2 focus-visible:ring-0 focus-visible:border-primary shadow-sm"
                        value={value}
                        onChange={e => onChange(e.target.value)}
                        placeholder={question.placeholder}
                    />
                    <span className="absolute bottom-4 right-4 text-xs text-muted-foreground">
                        {(value || '').length} chars
                    </span>
                </div>
            );
        case 'file-upload':
            return (
                <div
                    className={cn(
                        "border-2 border-dashed border-border hover:border-primary/50 rounded-2xl p-12 text-center cursor-pointer transition-all duration-200 bg-background hover:bg-accent/5 relative group"
                    )}
                    onClick={() => {
                        const fileInput = document.getElementById('file-upload-input') as HTMLInputElement;
                        fileInput?.click();
                    }}
                    onDragOver={(e) => { e.preventDefault(); e.currentTarget.classList.add('border-primary'); }}
                    onDragLeave={(e) => { e.preventDefault(); e.currentTarget.classList.remove('border-primary'); }}
                    onDrop={(e) => {
                        e.preventDefault();
                        e.currentTarget.classList.remove('border-primary');
                        const files = Array.from(e.dataTransfer.files);
                        if (files.length > 0) {
                            const newFileNames = files.map(f => f.name);
                            const current = Array.isArray(value) ? value : [];
                            // Filter duplicates
                            const unique = newFileNames.filter(n => !current.includes(n));
                            onChange([...current, ...unique]);
                        }
                    }}
                >
                    <input
                        id="file-upload-input"
                        type="file"
                        multiple
                        className="hidden"
                        onChange={(e) => {
                            if (e.target.files?.length) {
                                const files = Array.from(e.target.files);
                                const newFileNames = files.map(f => f.name);
                                const current = Array.isArray(value) ? value : [];
                                const unique = newFileNames.filter(n => !current.includes(n));
                                onChange([...current, ...unique]);
                                e.target.value = ''; // Reset
                            }
                        }}
                    />
                    <div className="flex justify-center mb-6 transition-transform duration-300 group-hover:-translate-y-1">
                        <div className="h-16 w-16 bg-muted rounded-2xl flex items-center justify-center shadow-sm">
                            <FileText className="h-8 w-8 text-muted-foreground" />
                        </div>
                    </div>
                    <p className="font-sans font-semibold text-foreground mb-2 text-lg">
                        Click or drag files here
                    </p>
                    <p className="font-sans text-sm text-muted-foreground max-w-xs mx-auto leading-relaxed">
                        Attach PDFs, docs, or strategy decks. We'll extract the wisdom.
                    </p>
                    {Array.isArray(value) && value.length > 0 && (
                        <div className="mt-8 text-left bg-card border border-border rounded-xl overflow-hidden shadow-sm animate-in slide-in-from-bottom-2">
                            <div className="bg-muted/30 px-4 py-2 border-b border-border flex justify-between items-center">
                                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Attached Files</span>
                                <span className="text-xs text-muted-foreground">{value.length} files</span>
                            </div>
                            <div className="divide-y divide-border">
                                {value.map((f: string, i: number) => (
                                    <div key={i} className="px-4 py-3 text-sm text-foreground flex items-center gap-3 hover:bg-muted/20 transition-colors group/file">
                                        <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center flex-shrink-0">
                                            <FileText className="h-4 w-4" />
                                        </div>
                                        <span className="flex-1 truncate font-medium">{f}</span>
                                        <button
                                            className="ml-auto h-6 w-6 flex items-center justify-center rounded-full hover:bg-destructive/10 hover:text-destructive text-muted-foreground transition-colors"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                onChange(value.filter((_: any, idx: number) => idx !== i));
                                            }}
                                        >
                                            <X className="h-3 w-3" />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            );
        case 'radio-cards':
            const optionCount = question.options?.length || 0;
            let gridClass = styles.radioCardsGrid;
            if (optionCount === 4) gridClass = styles.gridFour;
            if (optionCount >= 5) gridClass = styles.gridFive;

            return (
                <div
                    className={gridClass}
                    tabIndex={0}
                    onKeyDown={(e) => handleGridKeyDown(e, question.options || [])}
                    style={{ outline: 'none' }} // Custom focus handling
                >
                    {question.options?.map((opt, idx) => (
                        <div
                            key={opt.value}
                            className={`${styles.cardBase} ${value === opt.value ? styles.selected : ''} ${focusedCardIndex === idx ? 'ring-2 ring-primary ring-offset-2' : ''}`}
                            onClick={() => { onChange(opt.value); setTimeout(onEnter, 300); }}
                        >
                            <span className={styles.cardTitle}>{opt.label}</span>
                            {opt.description && <span className={styles.cardDesc}>{opt.description}</span>}
                            <div className={styles.checkmark}><Check className="h-3 w-3" /></div>
                            {focusedCardIndex === idx && (
                                <div className="absolute top-2 right-2 px-1.5 py-0.5 bg-primary text-primary-foreground text-[10px] uppercase font-bold tracking-wider rounded">
                                    Press Enter
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            );
        case 'choice-cards':
            const cOptionCount = question.options?.length || 0;
            let cGridClass = styles.choiceCardsGrid;
            if (cOptionCount === 4) cGridClass = styles.gridFour;
            if (cOptionCount >= 5) cGridClass = styles.gridFive;

            return (
                <div
                    className={cGridClass}
                    tabIndex={0}
                    onKeyDown={(e) => handleGridKeyDown(e, question.options || [])}
                    style={{ outline: 'none' }}
                >
                    {question.options?.map((opt, idx) => (
                        <div
                            key={opt.value}
                            className={`${styles.cardBase} ${value === opt.value ? styles.selected : ''} ${focusedCardIndex === idx ? 'ring-2 ring-primary ring-offset-2' : ''}`}
                            onClick={() => { onChange(opt.value); setTimeout(onEnter, 300); }}
                        >
                            <div className={styles.checkmark}><Check className="h-3 w-3" /></div>
                            <span className={styles.choiceCardLabel} style={{ fontSize: 18, fontWeight: 600, display: 'block', marginBottom: 8 }}>{opt.label}</span>
                            <span className={styles.cardDesc}>{opt.description}</span>
                            {focusedCardIndex === idx && (
                                <div className="absolute top-2 right-2 px-1.5 py-0.5 bg-primary text-primary-foreground text-[10px] uppercase font-bold tracking-wider rounded">
                                    Enter
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            );
        case 'multi-select':
            const vals = Array.isArray(value) ? value : [];
            const msOptionCount = question.options?.length || 0;
            let msGridClass = styles.multiSelectGrid;
            if (msOptionCount === 4) msGridClass = styles.gridFour;
            if (msOptionCount >= 5) msGridClass = styles.gridFive;

            return (
                <div
                    className={msGridClass}
                    tabIndex={0}
                    onKeyDown={(e) => handleGridKeyDown(e, question.options || [])}
                    style={{ outline: 'none' }}
                >
                    {question.options?.map((opt, idx) => {
                        const isSel = vals.includes(opt.value);
                        return (
                            <div
                                key={opt.value}
                                className={`${styles.cardBase} ${isSel ? styles.selected : ''} ${focusedCardIndex === idx ? 'ring-2 ring-primary ring-offset-2' : ''}`}
                                onClick={() => {
                                    const newVals = isSel ? vals.filter((v: string) => v !== opt.value) : [...vals, opt.value];
                                    onChange(newVals);
                                }}
                            >
                                <div className={styles.checkmark}><Check className="h-3 w-3" /></div>
                                <span className={styles.cardTitle}>{opt.label}</span>
                                {opt.description && <span className={styles.cardDesc}>{opt.description}</span>}
                                {focusedCardIndex === idx && (
                                    <div className="absolute top-2 right-2 px-1.5 py-0.5 bg-primary text-primary-foreground text-[10px] uppercase font-bold tracking-wider rounded">
                                        Enter to Toggle
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
            );
        default: return null;
    }
}
