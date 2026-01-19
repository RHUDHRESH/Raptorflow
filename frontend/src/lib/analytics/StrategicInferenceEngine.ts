import { Move, MoveCategory } from "@/components/moves/types";
import { differenceInDays, isAfter, subDays, parse } from "date-fns";

export interface StrategicGap {
    type: "critical" | "warning" | "opportunity";
    message: string;
    category?: MoveCategory;
    daysSince?: number;
    tasksInPeriod: number;
}

export interface Recommendation {
    title: string;
    description: string;
    moveCategory: MoveCategory;
    reason: string;
}

export interface RaptorScoreComponents {
    velocityScore: number;
    consistencyScore: number;
    varietyScore: number;
    focusScore: number;
    total: number;
}

export class StrategicInferenceEngine {
    private moves: Move[];
    private now: Date;
    private daysInRange: number;

    constructor(moves: Move[], daysInRange: number = 30) {
        this.moves = moves;
        this.now = new Date();
        this.daysInRange = daysInRange;
    }

    private getMovesInRange(): Move[] {
        const cutoff = subDays(this.now, this.daysInRange);
        return this.moves.filter(m =>
            (m.status === "completed" && m.endDate && isAfter(parse(m.endDate), cutoff)) ||
            (m.status === "active" && isAfter(parse(m.createdAt), cutoff))
        );
    }

    // Helper to count ALL completed tasks (Pillar, Cluster, Network) in the range for a specific category
    // This fixes the "Blind Spot" where DMs/Outreach were ignored.
    private getTaskVolumeByCategory(category: MoveCategory): number {
        const cutoff = subDays(this.now, this.daysInRange);
        let count = 0;

        this.moves.forEach(m => {
            // Only count tasks if the Move itself is related to the category?
            // OR should we check if specific tasks are channel-related?
            // For now, simplicity: Tasks inherit the Move's category.
            // If I do a "Capture" move, all its DMs are "Capture" tasks.
            if (m.category !== category) return;

            m.execution.forEach(day => {
                // Check if task completion date is within range?
                // We don't track exact completion date of tasks yet, only status.
                // Proxy: If move is active/completed recently, count its done tasks.
                // Better Proxy: Check move status.

                // If move is ancient, ignore.
                const moveDate = m.endDate ? parse(m.endDate) : parse(m.createdAt);
                if (!isAfter(moveDate, cutoff)) return;

                if (day.pillarTask.status === "done") count++;
                if (day.networkAction.status === "done") count++;
                day.clusterActions.forEach(a => {
                    if (a.status === "done") count++;
                });
            });
        });
        return count;
    }

    public calculateRaptorScore(): RaptorScoreComponents {
        const movesInRange = this.getMovesInRange();
        const activeMoves = this.moves.filter(m => m.status === "active");

        // 1. Velocity (30%):
        // Old: Just Number of Moves.
        // New: Moves + Task Volume (Hustle Factor).
        // Target: 1 Move OR 20 Tasks per week.
        const weeks = Math.max(this.daysInRange / 7, 1);
        const movesCount = movesInRange.length;

        let totalTasksInRange = 0;
        this.moves.forEach(m => {
            const moveDate = m.endDate ? parse(m.endDate) : parse(m.createdAt);
            const cutoff = subDays(this.now, this.daysInRange);
            if (isAfter(moveDate, cutoff)) {
                m.execution.forEach(day => {
                    if (day.pillarTask.status === "done") totalTasksInRange++;
                    if (day.networkAction.status === "done") totalTasksInRange++;
                    day.clusterActions.forEach(a => { if (a.status === "done") totalTasksInRange++; });
                });
            }
        });

        const targetMoves = weeks * 1;
        const targetTasks = weeks * 15; // 15 tasks/week is decent hustle

        const moveScore = Math.min((movesCount / targetMoves) * 100, 100);
        const taskScore = Math.min((totalTasksInRange / targetTasks) * 100, 100);

        // Velocity is max of Move speed or Task speed (allow manual hustle to count)
        const velocityScore = Math.max(Math.round(moveScore), Math.round(taskScore));


        // 2. Consistency (30%): Active moves on track (>0 progress)
        const onTrackCount = activeMoves.filter(m => (m?.progress ?? 0) > 0).length;
        const consistencyScore = activeMoves.length > 0
            ? Math.round((onTrackCount / activeMoves.length) * 100)
            : (velocityScore > 0 ? 100 : 0); // If no active but shipping, you are consistent.


        // 3. Variety (20%):
        // If range is short (7d), we don't expect variety.
        // If range is long (90d), we expect variety.
        let varietyScore = 100;
        if (this.daysInRange >= 30) {
            const categories = new Set(movesInRange.map(m => m.category));
            // Target: 2 categories for 30d, 3 for 90d
            const targetCats = this.daysInRange >= 60 ? 3 : 2;
            varietyScore = Math.min(Math.round((categories.size / targetCats) * 100), 100);
        }

        // 4. Focus (20%):
        // Reward having a clear "Main Effort".
        const catCounts: Record<string, number> = {};
        movesInRange.forEach(m => catCounts[m.category] = (catCounts[m.category] || 0) + 1);
        const maxCatCount = Math.max(...Object.values(catCounts), 0);
        const focusScore = movesInRange.length > 0
            ? (maxCatCount / movesInRange.length) >= 0.5 ? 100 : 70
            : 0;

        // Context-Aware Weighting: REMOVED by user request.
        // Returning to balanced weights.
        const total = Math.round(
            (velocityScore * 0.3) +
            (consistencyScore * 0.3) +
            (varietyScore * 0.2) +
            (focusScore * 0.2)
        );

        return { velocityScore, consistencyScore, varietyScore, focusScore, total };
    }

    public detectGaps(): StrategicGap[] {
        const gaps: StrategicGap[] = [];

        // "Realism" Check: Do we even have enough activity to judge?
        // If total activity is zero, return a "Start Engine" gap only.
        const movesInRange = this.getMovesInRange();
        if (movesInRange.length === 0) {
            gaps.push({
                type: "critical",
                message: "No execution detected in this period.",
                tasksInPeriod: 0
            });
            return gaps; // Return early if no activity
        }

        // Check specifics only if we have data
        // 1. Authority Check
        const authorityTasks = this.getTaskVolumeByCategory("authority");
        const daysSinceAuth = this.getDaysSinceCategory("authority");

        if (daysSinceAuth > 30 && authorityTasks < 5) {
            gaps.push({
                type: "warning",
                message: "Brand presence (Authority) is low.",
                category: "authority",
                daysSince: daysSinceAuth,
                tasksInPeriod: authorityTasks
            });
        }



        return gaps;
    }

    private getDaysSinceCategory(cat: MoveCategory): number {
        const completedMoves = this.moves.filter(m => m.status === "completed" && m.endDate);
        const movesInCat = completedMoves
            .filter(m => m.category === cat)
            .sort((a, b) => new Date(b.endDate!).getTime() - new Date(a.endDate!).getTime());

        if (movesInCat.length === 0) return 999;
        return differenceInDays(this.now, parse(movesInCat[0].endDate!));
    }


    public getCategoryScores(): Record<MoveCategory, number> {
        // The 5 Real Categories
        const scores: Record<MoveCategory, number> = {
            ignite: 0, capture: 0, authority: 0, repair: 0, rally: 0
        };

        const categories: MoveCategory[] = ['ignite', 'capture', 'authority', 'rally', 'repair'];

        categories.forEach(cat => {
            const moveCount = this.getMovesInRange().filter(m => m.category === cat).length;
            const taskCount = this.getTaskVolumeByCategory(cat);

            const weeks = Math.max(this.daysInRange / 7, 1);

            // Score Logic: 1 Move = 20 pts, 1 Task = 4 pts.
            const points = (moveCount * 20) + (taskCount * 4);
            const score = Math.min(Math.round((points / (weeks * 10)) * 100), 100);

            scores[cat] = score;
        });

        return scores;
    }

    public getNextBestAction(gaps: StrategicGap[]): Recommendation {
        // Priority 1: Warning
        const warning = gaps.find(g => g.type === "warning");
        if (warning && warning.category) {
            if (warning.category === "authority") {
                return {
                    title: "Founder Story",
                    description: "Share a 'Why I built this' moment.",
                    moveCategory: "authority",
                    reason: "Rebuild Brand Trust"
                };
            }
        }

        // Default to Sales Activation if no warnings, to keep things actionable.
        return {
            title: "Sales Activation",
            description: "Simple call-to-action to identify leads (formerly Hand-Raiser).",
            moveCategory: "capture",
            reason: "Generate Pipeline"
        };
    }
}
