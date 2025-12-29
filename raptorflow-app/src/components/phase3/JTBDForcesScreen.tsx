'use client';

import React from 'react';
import { JTBDForces, JTBDJob, JobType } from '@/lib/foundation';
import { Button } from '@/components/ui/button';
import { Plus, X, Star, ArrowRight } from 'lucide-react';
import { cn } from '@/lib/utils';

interface JTBDForcesScreenProps {
  jtbd: JTBDForces;
  onChange: (jtbd: JTBDForces) => void;
  onContinue: () => void;
}

interface ForceQuadrantProps {
  title: string;
  color: string;
  items: string[];
  onRemove: (index: number) => void;
  onAdd: (text: string) => void;
}

function ForceQuadrant({
  title,
  color,
  items,
  onRemove,
  onAdd,
}: ForceQuadrantProps) {
  const [isAdding, setIsAdding] = React.useState(false);
  const [newItem, setNewItem] = React.useState('');

  const handleAdd = () => {
    if (newItem.trim()) {
      onAdd(newItem.trim());
      setNewItem('');
      setIsAdding(false);
    }
  };

  const colorClasses: Record<
    string,
    { bg: string; border: string; text: string }
  > = {
    push: {
      bg: 'bg-red-50 dark:bg-red-950/30',
      border: 'border-red-200 dark:border-red-900',
      text: 'text-red-700 dark:text-red-400',
    },
    pull: {
      bg: 'bg-green-50 dark:bg-green-950/30',
      border: 'border-green-200 dark:border-green-900',
      text: 'text-green-700 dark:text-green-400',
    },
    anxiety: {
      bg: 'bg-amber-50 dark:bg-amber-950/30',
      border: 'border-amber-200 dark:border-amber-900',
      text: 'text-amber-700 dark:text-amber-400',
    },
    habit: {
      bg: 'bg-blue-50 dark:bg-blue-950/30',
      border: 'border-blue-200 dark:border-blue-900',
      text: 'text-blue-700 dark:text-blue-400',
    },
  };

  const colors = colorClasses[color] || colorClasses.push;

  return (
    <div className={cn('rounded-xl p-5 border-2', colors.bg, colors.border)}>
      <h3
        className={cn(
          'font-semibold text-sm uppercase tracking-wider mb-3',
          colors.text
        )}
      >
        {title}
      </h3>
      <div className="space-y-2">
        {items.slice(0, 3).map((item, i) => (
          <div key={i} className="flex items-start gap-2 group">
            <span className="text-sm text-foreground leading-relaxed flex-1">
              {item}
            </span>
            <button
              onClick={() => onRemove(i)}
              className="opacity-0 group-hover:opacity-100 p-1 hover:bg-destructive/10 rounded transition-all"
            >
              <X className="h-3 w-3 text-muted-foreground" />
            </button>
          </div>
        ))}

        {items.length === 0 && !isAdding && (
          <p className="text-sm text-muted-foreground italic">
            No items detected
          </p>
        )}

        {isAdding ? (
          <div className="flex gap-2 mt-2">
            <input
              type="text"
              value={newItem}
              onChange={(e) => setNewItem(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAdd()}
              placeholder="Add item..."
              className="flex-1 text-sm px-3 py-2 rounded-lg border bg-background"
              autoFocus
            />
            <Button size="sm" onClick={handleAdd}>
              Add
            </Button>
          </div>
        ) : (
          items.length < 3 && (
            <button
              onClick={() => setIsAdding(true)}
              className="text-xs text-muted-foreground hover:text-foreground flex items-center gap-1 mt-2"
            >
              <Plus className="h-3 w-3" /> Add
            </button>
          )
        )}
      </div>
    </div>
  );
}

function JobCard({
  job,
  onSetPrimary,
  onRemove,
}: {
  job: JTBDJob;
  onSetPrimary: () => void;
  onRemove: () => void;
}) {
  const typeColors: Record<JobType, string> = {
    functional:
      'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400',
    emotional:
      'bg-pink-100 text-pink-700 dark:bg-pink-900/30 dark:text-pink-400',
    social: 'bg-cyan-100 text-cyan-700 dark:bg-cyan-900/30 dark:text-cyan-400',
  };

  return (
    <div
      className={cn(
        'p-4 rounded-xl border-2 transition-all',
        job.isPrimary
          ? 'border-primary bg-primary/5'
          : 'border-border hover:border-primary/30'
      )}
    >
      <div className="flex items-start gap-3">
        <button
          onClick={onSetPrimary}
          className={cn(
            'mt-0.5 p-1 rounded-full transition-colors',
            job.isPrimary
              ? 'text-primary'
              : 'text-muted-foreground hover:text-primary'
          )}
        >
          <Star className={cn('h-4 w-4', job.isPrimary && 'fill-current')} />
        </button>
        <div className="flex-1">
          <span
            className={cn(
              'text-xs px-2 py-0.5 rounded-full',
              typeColors[job.type]
            )}
          >
            {job.type}
          </span>
          <p className="mt-2 text-foreground">{job.statement}</p>
        </div>
        <button
          onClick={onRemove}
          className="p-1 hover:bg-destructive/10 rounded"
        >
          <X className="h-4 w-4 text-muted-foreground" />
        </button>
      </div>
    </div>
  );
}

export function JTBDForcesScreen({
  jtbd,
  onChange,
  onContinue,
}: JTBDForcesScreenProps) {
  const updateForce = (force: keyof typeof jtbd.forces, items: string[]) => {
    onChange({
      ...jtbd,
      forces: { ...jtbd.forces, [force]: items },
    });
  };

  const removeFromForce = (force: keyof typeof jtbd.forces, index: number) => {
    const items = [...jtbd.forces[force]];
    items.splice(index, 1);
    updateForce(force, items);
  };

  const addToForce = (force: keyof typeof jtbd.forces, text: string) => {
    updateForce(force, [...jtbd.forces[force], text]);
  };

  const setJobPrimary = (jobId: string) => {
    onChange({
      ...jtbd,
      jobs: jtbd.jobs.map((j) => ({ ...j, isPrimary: j.id === jobId })),
    });
  };

  const removeJob = (jobId: string) => {
    onChange({
      ...jtbd,
      jobs: jtbd.jobs.filter((j) => j.id !== jobId),
    });
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-serif font-bold text-foreground">
          The Progress Story
        </h1>
        <p className="text-muted-foreground max-w-lg mx-auto">
          These are the forces that drive customers to switch. Edit what doesn't
          feel right.
        </p>
      </div>

      {/* Jobs Section */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold">Jobs to be Done</h2>
        <div className="grid gap-3 max-w-2xl">
          {jtbd.jobs.map((job) => (
            <JobCard
              key={job.id}
              job={job}
              onSetPrimary={() => setJobPrimary(job.id)}
              onRemove={() => removeJob(job.id)}
            />
          ))}
        </div>
      </div>

      {/* Forces Quadrants */}
      <div className="grid grid-cols-2 gap-4 max-w-3xl mx-auto">
        <ForceQuadrant
          title="Push (What's breaking)"
          color="push"
          items={jtbd.forces.push}
          onRemove={(i) => removeFromForce('push', i)}
          onAdd={(t) => addToForce('push', t)}
        />
        <ForceQuadrant
          title="Pull (What they want)"
          color="pull"
          items={jtbd.forces.pull}
          onRemove={(i) => removeFromForce('pull', i)}
          onAdd={(t) => addToForce('pull', t)}
        />
        <ForceQuadrant
          title="Anxiety (What scares them)"
          color="anxiety"
          items={jtbd.forces.anxiety}
          onRemove={(i) => removeFromForce('anxiety', i)}
          onAdd={(t) => addToForce('anxiety', t)}
        />
        <ForceQuadrant
          title="Habit (What keeps them stuck)"
          color="habit"
          items={jtbd.forces.habit}
          onRemove={(i) => removeFromForce('habit', i)}
          onAdd={(t) => addToForce('habit', t)}
        />
      </div>

      {/* Continue Button */}
      <div className="flex justify-center pt-4">
        <Button
          size="lg"
          onClick={onContinue}
          className="px-8 py-6 text-lg rounded-xl"
        >
          Continue <ArrowRight className="h-5 w-5 ml-2" />
        </Button>
      </div>
    </div>
  );
}
