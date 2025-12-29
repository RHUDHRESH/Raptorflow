'use client';

import React from 'react';
import { ICPPersona, PersonaItem, DataConfidence } from '@/lib/foundation';
import { Button } from '@/components/ui/button';
import {
  ArrowRight,
  Check,
  AlertCircle,
  HelpCircle,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface PersonaStackProps {
  personas: ICPPersona[];
  icpName: string;
  onChange: (personas: ICPPersona[]) => void;
  onContinue: () => void;
}

function ConfidenceBadge({ confidence }: { confidence: DataConfidence }) {
  const config: Record<
    DataConfidence,
    { bg: string; text: string; label: string }
  > = {
    proven: {
      bg: 'bg-green-100 dark:bg-green-900/30',
      text: 'text-green-700 dark:text-green-400',
      label: 'Proven',
    },
    inferred: {
      bg: 'bg-amber-100 dark:bg-amber-900/30',
      text: 'text-amber-700 dark:text-amber-400',
      label: 'Inferred',
    },
    assumed: {
      bg: 'bg-red-100 dark:bg-red-900/30',
      text: 'text-red-700 dark:text-red-400',
      label: 'Assumed',
    },
  };

  const { bg, text, label } = config[confidence];

  return (
    <span className={cn('text-xs px-2 py-0.5 rounded-full', bg, text)}>
      {label}
    </span>
  );
}

function PersonaCard({
  persona,
  onChange,
}: {
  persona: ICPPersona;
  onChange: (persona: ICPPersona) => void;
}) {
  const [expanded, setExpanded] = React.useState(false);

  const toggleConfidence = (field: 'goals' | 'objections', index: number) => {
    const items = [...persona[field]];
    const nextConfidence: Record<DataConfidence, DataConfidence> = {
      proven: 'inferred',
      inferred: 'assumed',
      assumed: 'proven',
    };
    items[index] = {
      ...items[index],
      confidence: nextConfidence[items[index].confidence],
    };
    onChange({ ...persona, [field]: items });
  };

  return (
    <div className="bg-card border rounded-xl overflow-hidden">
      {/* Header */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full p-4 flex items-center justify-between hover:bg-muted/50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
            <span className="text-primary font-bold">
              {persona.role.charAt(0)}
            </span>
          </div>
          <span className="font-semibold">{persona.role}</span>
        </div>
        {expanded ? (
          <ChevronUp className="h-4 w-4" />
        ) : (
          <ChevronDown className="h-4 w-4" />
        )}
      </button>

      {expanded && (
        <div className="p-4 pt-0 space-y-4">
          {/* Goals */}
          <div>
            <h4 className="text-sm font-medium text-muted-foreground mb-2">
              Goals
            </h4>
            <div className="space-y-2">
              {persona.goals.map((goal, i) => (
                <div key={i} className="flex items-center gap-2">
                  <Check className="h-3 w-3 text-green-500" />
                  <span className="flex-1 text-sm">{goal.text}</span>
                  <button onClick={() => toggleConfidence('goals', i)}>
                    <ConfidenceBadge confidence={goal.confidence} />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* KPIs */}
          {persona.kpis.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-muted-foreground mb-2">
                KPIs
              </h4>
              <div className="flex flex-wrap gap-2">
                {persona.kpis.map((kpi, i) => (
                  <span key={i} className="text-xs bg-muted px-2 py-1 rounded">
                    {kpi}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Objections */}
          <div>
            <h4 className="text-sm font-medium text-muted-foreground mb-2">
              Objections
            </h4>
            <div className="space-y-2">
              {persona.objections.map((obj, i) => (
                <div key={i} className="flex items-center gap-2">
                  <AlertCircle className="h-3 w-3 text-amber-500" />
                  <span className="flex-1 text-sm">{obj.text}</span>
                  <button onClick={() => toggleConfidence('objections', i)}>
                    <ConfidenceBadge confidence={obj.confidence} />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Proof Needs */}
          {persona.proofNeeds.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-muted-foreground mb-2">
                Proof They Need
              </h4>
              <div className="flex flex-wrap gap-2">
                {persona.proofNeeds.map((proof, i) => (
                  <span
                    key={i}
                    className="text-xs bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 px-2 py-1 rounded"
                  >
                    {proof}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Language */}
          {persona.language.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-muted-foreground mb-2">
                Language They Use
              </h4>
              <div className="flex flex-wrap gap-2">
                {persona.language.map((word, i) => (
                  <span
                    key={i}
                    className="text-xs bg-muted px-2 py-1 rounded italic"
                  >
                    "{word}"
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export function PersonaStack({
  personas,
  icpName,
  onChange,
  onContinue,
}: PersonaStackProps) {
  const handlePersonaChange = (personaId: string, persona: ICPPersona) => {
    onChange(personas.map((p) => (p.id === personaId ? persona : p)));
  };

  const provenCount = personas.reduce((acc, p) => {
    return (
      acc +
      p.goals.filter((g) => g.confidence === 'proven').length +
      p.objections.filter((o) => o.confidence === 'proven').length
    );
  }, 0);

  const totalCount = personas.reduce((acc, p) => {
    return acc + p.goals.length + p.objections.length;
  }, 0);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-serif font-bold text-foreground">
          Persona Stack: {icpName}
        </h1>
        <p className="text-muted-foreground max-w-lg mx-auto">
          Personas are roles, not bios. Every claim is tagged as proven,
          inferred, or assumed.
        </p>
      </div>

      {/* Confidence Summary */}
      <div className="max-w-md mx-auto bg-card border rounded-xl p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium">Research-backed Claims</span>
          <span
            className={cn(
              'text-sm font-bold',
              provenCount === totalCount
                ? 'text-green-600'
                : provenCount > totalCount / 2
                  ? 'text-amber-600'
                  : 'text-red-600'
            )}
          >
            {provenCount} / {totalCount}
          </span>
        </div>
        <div className="h-2 bg-muted rounded-full overflow-hidden">
          <div
            className="h-full bg-green-500 rounded-full"
            style={{
              width:
                totalCount > 0 ? `${(provenCount / totalCount) * 100}%` : '0%',
            }}
          />
        </div>
        <p className="text-xs text-muted-foreground mt-2">
          Click badges to change confidence levels
        </p>
      </div>

      {/* Personas */}
      <div className="space-y-4 max-w-2xl mx-auto">
        {personas.map((persona) => (
          <PersonaCard
            key={persona.id}
            persona={persona}
            onChange={(p) => handlePersonaChange(persona.id, p)}
          />
        ))}
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
