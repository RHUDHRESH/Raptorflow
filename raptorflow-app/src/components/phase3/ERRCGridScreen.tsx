'use client';

import React from 'react';
import { ERRCGrid, ERRCItem } from '@/lib/foundation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ArrowRight, Plus, X, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ERRCGridScreenProps {
  errc: ERRCGrid;
  onChange: (errc: ERRCGrid) => void;
  onContinue: () => void;
}

interface ERRCColumnProps {
  title: string;
  subtitle: string;
  color: string;
  items: ERRCItem[];
  onAdd: (item: ERRCItem) => void;
  onRemove: (index: number) => void;
  onEdit: (index: number, item: ERRCItem) => void;
}

function ERRCColumn({
  title,
  subtitle,
  color,
  items,
  onAdd,
  onRemove,
  onEdit,
}: ERRCColumnProps) {
  const [isAdding, setIsAdding] = React.useState(false);
  const [newFactor, setNewFactor] = React.useState('');
  const [newReason, setNewReason] = React.useState('');

  const colorClasses: Record<
    string,
    { bg: string; border: string; text: string; pill: string }
  > = {
    eliminate: {
      bg: 'bg-red-50/50 dark:bg-red-950/20',
      border: 'border-red-200 dark:border-red-900',
      text: 'text-red-700 dark:text-red-400',
      pill: 'bg-red-100 text-red-700 dark:bg-red-900/50 dark:text-red-400',
    },
    reduce: {
      bg: 'bg-amber-50/50 dark:bg-amber-950/20',
      border: 'border-amber-200 dark:border-amber-900',
      text: 'text-amber-700 dark:text-amber-400',
      pill: 'bg-amber-100 text-amber-700 dark:bg-amber-900/50 dark:text-amber-400',
    },
    raise: {
      bg: 'bg-blue-50/50 dark:bg-blue-950/20',
      border: 'border-blue-200 dark:border-blue-900',
      text: 'text-blue-700 dark:text-blue-400',
      pill: 'bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-400',
    },
    create: {
      bg: 'bg-green-50/50 dark:bg-green-950/20',
      border: 'border-green-200 dark:border-green-900',
      text: 'text-green-700 dark:text-green-400',
      pill: 'bg-green-100 text-green-700 dark:bg-green-900/50 dark:text-green-400',
    },
  };

  const colors = colorClasses[color] || colorClasses.eliminate;

  const handleAdd = () => {
    if (newFactor.trim()) {
      onAdd({ factor: newFactor.trim(), reason: newReason.trim() });
      setNewFactor('');
      setNewReason('');
      setIsAdding(false);
    }
  };

  return (
    <div className={cn('rounded-xl border-2 overflow-hidden', colors.border)}>
      <div className={cn('p-4', colors.bg)}>
        <h3 className={cn('font-bold text-lg', colors.text)}>{title}</h3>
        <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>
      </div>

      <div className="p-4 space-y-3 min-h-[200px]">
        {items.map((item, i) => (
          <div key={i} className="p-3 bg-card rounded-lg border group">
            <div className="flex items-start gap-2">
              <div className="flex-1">
                <span
                  className={cn(
                    'text-xs px-2 py-0.5 rounded-full',
                    colors.pill
                  )}
                >
                  {item.factor}
                </span>
                {item.reason && (
                  <p className="text-xs text-muted-foreground mt-2">
                    {item.reason}
                  </p>
                )}
              </div>
              <button
                onClick={() => onRemove(i)}
                className="opacity-0 group-hover:opacity-100 p-1 hover:bg-destructive/10 rounded transition-all"
              >
                <X className="h-3 w-3 text-muted-foreground" />
              </button>
            </div>
          </div>
        ))}

        {items.length === 0 && !isAdding && (
          <div className="text-center py-8 text-muted-foreground">
            <AlertCircle className="h-8 w-8 mx-auto mb-2 opacity-30" />
            <p className="text-sm">Add at least one item</p>
          </div>
        )}

        {isAdding ? (
          <div className="space-y-2 p-3 bg-muted/50 rounded-lg">
            <Input
              placeholder="Factor name"
              value={newFactor}
              onChange={(e) => setNewFactor(e.target.value)}
              className="text-sm"
              autoFocus
            />
            <Input
              placeholder="Why? (optional)"
              value={newReason}
              onChange={(e) => setNewReason(e.target.value)}
              className="text-sm"
            />
            <div className="flex gap-2 justify-end">
              <Button
                size="sm"
                variant="ghost"
                onClick={() => setIsAdding(false)}
              >
                Cancel
              </Button>
              <Button size="sm" onClick={handleAdd}>
                Add
              </Button>
            </div>
          </div>
        ) : (
          <button
            onClick={() => setIsAdding(true)}
            className="w-full p-3 border-2 border-dashed rounded-lg text-sm text-muted-foreground hover:text-foreground hover:border-primary/30 transition-all flex items-center justify-center gap-2"
          >
            <Plus className="h-4 w-4" /> Add
          </button>
        )}
      </div>
    </div>
  );
}

export function ERRCGridScreen({
  errc,
  onChange,
  onContinue,
}: ERRCGridScreenProps) {
  const isValid =
    errc.eliminate.length >= 1 &&
    errc.reduce.length >= 1 &&
    errc.raise.length >= 1 &&
    errc.create.length >= 1;

  const updateColumn = (column: keyof ERRCGrid, items: ERRCItem[]) => {
    onChange({ ...errc, [column]: items });
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-serif font-bold text-foreground">
          ERRC Grid — Trade-off Decisions
        </h1>
        <p className="text-muted-foreground max-w-lg mx-auto">
          Real strategy means choosing what NOT to do. You must have at least
          one item in each column.
        </p>
      </div>

      {/* Validation Warning */}
      {!isValid && (
        <div className="max-w-3xl mx-auto bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900 rounded-xl p-4 flex items-center gap-3">
          <AlertCircle className="h-5 w-5 text-amber-600" />
          <p className="text-sm text-amber-700 dark:text-amber-400">
            Each column needs at least one item to continue. Real Blue Ocean
            strategy requires trade-offs.
          </p>
        </div>
      )}

      {/* ERRC Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 max-w-5xl mx-auto">
        <ERRCColumn
          title="Eliminate"
          subtitle="What should we stop doing entirely?"
          color="eliminate"
          items={errc.eliminate}
          onAdd={(item) => updateColumn('eliminate', [...errc.eliminate, item])}
          onRemove={(i) =>
            updateColumn(
              'eliminate',
              errc.eliminate.filter((_, idx) => idx !== i)
            )
          }
          onEdit={(i, item) =>
            updateColumn(
              'eliminate',
              errc.eliminate.map((el, idx) => (idx === i ? item : el))
            )
          }
        />
        <ERRCColumn
          title="Reduce"
          subtitle="What should we do less of?"
          color="reduce"
          items={errc.reduce}
          onAdd={(item) => updateColumn('reduce', [...errc.reduce, item])}
          onRemove={(i) =>
            updateColumn(
              'reduce',
              errc.reduce.filter((_, idx) => idx !== i)
            )
          }
          onEdit={(i, item) =>
            updateColumn(
              'reduce',
              errc.reduce.map((el, idx) => (idx === i ? item : el))
            )
          }
        />
        <ERRCColumn
          title="Raise"
          subtitle="What should we do more of?"
          color="raise"
          items={errc.raise}
          onAdd={(item) => updateColumn('raise', [...errc.raise, item])}
          onRemove={(i) =>
            updateColumn(
              'raise',
              errc.raise.filter((_, idx) => idx !== i)
            )
          }
          onEdit={(i, item) =>
            updateColumn(
              'raise',
              errc.raise.map((el, idx) => (idx === i ? item : el))
            )
          }
        />
        <ERRCColumn
          title="Create"
          subtitle="What new value should we invent?"
          color="create"
          items={errc.create}
          onAdd={(item) => updateColumn('create', [...errc.create, item])}
          onRemove={(i) =>
            updateColumn(
              'create',
              errc.create.filter((_, idx) => idx !== i)
            )
          }
          onEdit={(i, item) =>
            updateColumn(
              'create',
              errc.create.map((el, idx) => (idx === i ? item : el))
            )
          }
        />
      </div>

      {/* Continue Button */}
      <div className="flex justify-center pt-4">
        <Button
          size="lg"
          onClick={onContinue}
          disabled={!isValid}
          className="px-8 py-6 text-lg rounded-xl"
        >
          Continue <ArrowRight className="h-5 w-5 ml-2" />
        </Button>
      </div>
    </div>
  );
}
