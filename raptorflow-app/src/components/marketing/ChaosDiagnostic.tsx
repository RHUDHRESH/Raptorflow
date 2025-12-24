'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';

interface QuizQuestion {
    id: string;
    question: string;
    options: { value: number; label: string }[];
}

const questions: QuizQuestion[] = [
    {
        id: 'tools',
        question: 'How many tools do you use for marketing?',
        options: [
            { value: 0, label: '1-2 (streamlined)' },
            { value: 30, label: '3-5 (manageable)' },
            { value: 60, label: '6-10 (chaotic)' },
            { value: 100, label: '10+ (help me)' },
        ],
    },
    {
        id: 'icp',
        question: 'Do you have a documented Ideal Customer Profile?',
        options: [
            { value: 0, label: 'Yes, detailed and updated' },
            { value: 40, label: 'Yes, but outdated' },
            { value: 70, label: 'Sort of, in my head' },
            { value: 100, label: 'What is an ICP?' },
        ],
    },
    {
        id: 'consistency',
        question: 'When did you last post content consistently for 4+ weeks?',
        options: [
            { value: 0, label: 'Currently doing it' },
            { value: 30, label: 'Within the last month' },
            { value: 60, label: 'A few months ago' },
            { value: 100, label: 'Never / Cannot remember' },
        ],
    },
    {
        id: 'strategy',
        question: 'How would you describe your marketing strategy?',
        options: [
            { value: 0, label: 'Clear 90-day plan with milestones' },
            { value: 40, label: 'General direction, flexible' },
            { value: 70, label: 'Week-by-week survival' },
            { value: 100, label: 'What strategy?' },
        ],
    },
    {
        id: 'tracking',
        question: 'How do you track marketing results?',
        options: [
            { value: 0, label: 'Unified dashboard with clear KPIs' },
            { value: 30, label: 'Spreadsheets and scattered analytics' },
            { value: 70, label: 'Check social media likes sometimes' },
            { value: 100, label: 'I do not track anything' },
        ],
    },
    {
        id: 'time',
        question: 'How much time do you spend deciding what to post?',
        options: [
            { value: 0, label: 'Minutes (it is planned)' },
            { value: 40, label: '30-60 minutes per piece' },
            { value: 70, label: 'Hours of staring at blank screen' },
            { value: 100, label: 'I avoid it entirely' },
        ],
    },
];

interface DiagnosisResult {
    score: number;
    level: 'low' | 'medium' | 'high' | 'critical';
    title: string;
    description: string;
    painPoints: string[];
    solutions: { feature: string; benefit: string }[];
}

function getDiagnosis(score: number): DiagnosisResult {
    if (score <= 25) {
        return {
            score,
            level: 'low',
            title: 'Marketing Machine',
            description: 'You are already running a tight operation. RaptorFlow can help you scale faster.',
            painPoints: ['Scaling without losing quality', 'Team coordination'],
            solutions: [
                { feature: 'Muse', benefit: '10x content output without losing your voice' },
                { feature: 'Matrix', benefit: 'Scale visibility across campaigns' },
            ],
        };
    } else if (score <= 50) {
        return {
            score,
            level: 'medium',
            title: 'Organized Chaos',
            description: 'You have systems, but gaps are showing. Time to close them before they widen.',
            painPoints: ['Inconsistent execution', 'Unclear ICP', 'Tool fragmentation'],
            solutions: [
                { feature: 'Foundation', benefit: 'Lock in your positioning once and for all' },
                { feature: 'Campaigns', benefit: '90-day arcs that compound instead of reset' },
                { feature: 'Moves', benefit: 'Weekly execution packets you can actually ship' },
            ],
        };
    } else if (score <= 75) {
        return {
            score,
            level: 'high',
            title: 'Marketing Swamp',
            description: 'You are stuck in the classic founder trap: too busy building to market consistently.',
            painPoints: ['No clear positioning', 'Random content', 'Zero tracking', 'Tool overload'],
            solutions: [
                { feature: 'Foundation', benefit: 'Extract strategy from your head in 10 minutes' },
                { feature: 'Cohorts', benefit: 'Know exactly who you are talking to' },
                { feature: 'Moves', benefit: 'Stop wondering what to post' },
                { feature: 'Matrix', benefit: 'One dashboard instead of twelve' },
            ],
        };
    } else {
        return {
            score,
            level: 'critical',
            title: 'Marketing Emergency',
            description: 'You are losing customers to competitors with worse products but clearer messaging.',
            painPoints: ['Complete chaos', 'No system', 'Random acts of marketing', 'Burnout imminent'],
            solutions: [
                { feature: 'Foundation', benefit: 'Build your BrandKit from scratch' },
                { feature: 'Cohorts', benefit: 'Define ICPs that actually convert' },
                { feature: 'Campaigns', benefit: 'Create your first 90-day war plan' },
                { feature: 'Moves', benefit: 'Get 7 execution tasks every week' },
                { feature: 'Muse', benefit: 'AI that writes in your voice' },
            ],
        };
    }
}

export function ChaosDiagnostic() {
    const [currentQuestion, setCurrentQuestion] = useState(0);
    const [answers, setAnswers] = useState<Record<string, number>>({});
    const [showResult, setShowResult] = useState(false);
    const [isAnimating, setIsAnimating] = useState(false);

    const handleAnswer = (questionId: string, value: number) => {
        setAnswers((prev) => ({ ...prev, [questionId]: value }));
        setIsAnimating(true);

        setTimeout(() => {
            if (currentQuestion < questions.length - 1) {
                setCurrentQuestion((prev) => prev + 1);
            } else {
                setShowResult(true);
            }
            setIsAnimating(false);
        }, 300);
    };

    const totalScore = Math.round(
        Object.values(answers).reduce((a, b) => a + b, 0) / questions.length
    );

    const diagnosis = getDiagnosis(totalScore);

    const resetQuiz = () => {
        setCurrentQuestion(0);
        setAnswers({});
        setShowResult(false);
    };

    if (showResult) {
        return (
            <div className="w-full max-w-2xl mx-auto">
                {/* Score Display */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center">
                        <div className={`
              relative h-32 w-32 rounded-full flex items-center justify-center
              ${diagnosis.level === 'low' ? 'bg-green-500/10 text-green-600' : ''}
              ${diagnosis.level === 'medium' ? 'bg-yellow-500/10 text-yellow-600' : ''}
              ${diagnosis.level === 'high' ? 'bg-orange-500/10 text-orange-600' : ''}
              ${diagnosis.level === 'critical' ? 'bg-red-500/10 text-red-600' : ''}
            `}>
                            <div className="text-center">
                                <div className="font-mono text-4xl font-bold">{totalScore}</div>
                                <div className="text-xs uppercase tracking-wider opacity-70">Chaos Score</div>
                            </div>
                            {/* Circular progress indicator */}
                            <svg className="absolute inset-0 -rotate-90" viewBox="0 0 100 100">
                                <circle
                                    cx="50"
                                    cy="50"
                                    r="45"
                                    fill="none"
                                    stroke="currentColor"
                                    strokeWidth="4"
                                    strokeDasharray={`${totalScore * 2.83} 283`}
                                    className="opacity-30"
                                />
                            </svg>
                        </div>
                    </div>
                    <h3 className="font-display text-2xl font-medium mt-6">{diagnosis.title}</h3>
                    <p className="text-muted-foreground mt-2">{diagnosis.description}</p>
                </div>

                {/* Pain Points */}
                <div className="rounded-xl border border-border bg-card p-6 mb-6">
                    <h4 className="font-semibold mb-4">Your Pain Points</h4>
                    <div className="flex flex-wrap gap-2">
                        {diagnosis.painPoints.map((pain) => (
                            <span
                                key={pain}
                                className="px-3 py-1 rounded-full bg-destructive/10 text-destructive text-sm"
                            >
                                {pain}
                            </span>
                        ))}
                    </div>
                </div>

                {/* Prescription */}
                <div className="rounded-xl border border-border bg-card p-6 mb-8">
                    <h4 className="font-semibold mb-4">Your Prescription</h4>
                    <ul className="space-y-3">
                        {diagnosis.solutions.map((solution) => (
                            <li key={solution.feature} className="flex items-start gap-3">
                                <div className="h-6 w-6 rounded-full bg-foreground flex items-center justify-center flex-shrink-0 mt-0.5">
                                    <svg className="h-3 w-3 text-background" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                                    </svg>
                                </div>
                                <div>
                                    <span className="font-medium">{solution.feature}:</span>{' '}
                                    <span className="text-muted-foreground">{solution.benefit}</span>
                                </div>
                            </li>
                        ))}
                    </ul>
                </div>

                {/* CTAs */}
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                    <Button size="lg" className="h-12 px-8 rounded-xl">
                        Start Free — Fix Your Chaos
                    </Button>
                    <Button variant="outline" size="lg" className="h-12 px-8 rounded-xl" onClick={resetQuiz}>
                        Retake Quiz
                    </Button>
                </div>
            </div>
        );
    }

    const question = questions[currentQuestion];
    const progress = ((currentQuestion + 1) / questions.length) * 100;

    return (
        <div className="w-full max-w-2xl mx-auto">
            {/* Progress */}
            <div className="mb-8">
                <div className="flex items-center justify-between text-sm text-muted-foreground mb-2">
                    <span>Question {currentQuestion + 1} of {questions.length}</span>
                    <span>{Math.round(progress)}%</span>
                </div>
                <div className="h-1 bg-muted rounded-full overflow-hidden">
                    <div
                        className="h-full bg-foreground transition-all duration-500 ease-out"
                        style={{ width: `${progress}%` }}
                    />
                </div>
            </div>

            {/* Question */}
            <div className={`transition-all duration-300 ${isAnimating ? 'opacity-0 translate-x-4' : 'opacity-100 translate-x-0'}`}>
                <h3 className="font-display text-2xl font-medium mb-8 text-center">
                    {question.question}
                </h3>

                {/* Options */}
                <div className="grid gap-3">
                    {question.options.map((option) => (
                        <button
                            key={option.value}
                            onClick={() => handleAnswer(question.id, option.value)}
                            className="w-full p-4 rounded-xl border border-border bg-card text-left hover:border-foreground/50 hover:bg-muted/50 transition-all duration-200 group"
                        >
                            <span className="group-hover:translate-x-1 transition-transform duration-200 inline-block">
                                {option.label}
                            </span>
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
}
