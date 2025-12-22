'use client';

import React, { useState } from 'react';
import { FoundationData, ConfessionData } from '@/lib/foundation';
import { Button } from '@/components/ui/button';
import styles from './Steps.module.css';

interface StepProps {
    data: FoundationData;
    updateData: <K extends keyof FoundationData>(section: K, value: FoundationData[K]) => void;
    onNext: () => void;
    onBack: () => void;
}

const QUESTIONS: { field: keyof ConfessionData; question: string; hint: string }[] = [
    {
        field: 'expensiveProblem',
        question: "What expensive problem are you trying to solve that might just need different words?",
        hint: "Eurostar spent £6B to speed up trains. They could have added Wi-Fi so time passes faster. What's your version?",
    },
    {
        field: 'embarrassingTruth',
        question: "What are your customers embarrassed to admit about why they buy?",
        hint: "People buy hybrids to look like they care about the planet, not just to save it.",
    },
    {
        field: 'stupidIdea',
        question: "What 'stupid' thing could work because nobody is doing it?",
        hint: "Red Bull tastes terrible and is expensive. Every logical rule says it should fail. What's your counterintuitive idea?",
    },
    {
        field: 'signaling',
        question: "What does your product signal to peers, bosses, or neighbors?",
        hint: "Beyond the utility—what status, competence, or taste does buying you communicate?",
    },
    {
        field: 'friction',
        question: "Where is the friction—and should you add some?",
        hint: "Cake mix was too easy ('just add water'). General Mills had to add 'add an egg' so people felt like cooking.",
    },
];

export function StepConfession({ data, updateData, onNext, onBack }: StepProps) {
    const [currentQ, setCurrentQ] = useState(0);
    const confession = data.confession;

    const handleChange = (field: keyof ConfessionData, value: string) => {
        updateData('confession', { ...confession, [field]: value });
    };

    const question = QUESTIONS[currentQ];
    const isLastQuestion = currentQ === QUESTIONS.length - 1;
    const hasAnswer = confession[question.field]?.trim().length > 0;

    const handleNext = () => {
        if (isLastQuestion) {
            onNext();
        } else {
            setCurrentQ(currentQ + 1);
        }
    };

    const handlePrev = () => {
        if (currentQ > 0) {
            setCurrentQ(currentQ - 1);
        } else {
            onBack();
        }
    };

    return (
        <div className={styles.step}>
            <div className={styles.stepHeader}>
                <h2 className={styles.stepTitle}>The Confession</h2>
                <p className={styles.stepSubtitle}>
                    Question {currentQ + 1} of {QUESTIONS.length}
                </p>
            </div>

            <div className={styles.questionCard}>
                <p className={styles.questionText}>{question.question}</p>
                <p className={styles.questionHint}>{question.hint}</p>

                <textarea
                    className={styles.textarea}
                    value={confession[question.field]}
                    onChange={(e) => handleChange(question.field, e.target.value)}
                    placeholder="Type your answer..."
                    rows={4}
                />
            </div>

            <div className={styles.actions}>
                <Button variant="secondary" onClick={handlePrev}>
                    <BackIcon />
                    Back
                </Button>

                <div className={styles.actionRight}>
                    {!hasAnswer && !isLastQuestion && (
                        <button
                            type="button"
                            className={styles.skipButton}
                            onClick={handleNext}
                        >
                            Skip
                        </button>
                    )}
                    <Button variant="default" onClick={handleNext}>
                        {isLastQuestion ? 'Continue' : 'Next Question'}
                        <ArrowIcon />
                    </Button>
                </div>
            </div>
        </div>
    );
}

function ArrowIcon() {
    return (
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M3 8H13M13 8L9 4M13 8L9 12" />
        </svg>
    );
}

function BackIcon() {
    return (
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M13 8H3M3 8L7 4M3 8L7 12" />
        </svg>
    );
}
