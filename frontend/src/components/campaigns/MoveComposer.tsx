"use client";

import { useState, useCallback } from 'react';
import {
  DragDropContext,
  Droppable,
  Draggable,
  DropResult,
  DroppableProvided,
  DraggableProvided,
  DraggableStateSnapshot
} from '@hello-pangea/dnd';
import {
  Plus,
  Settings,
  Play,
  Pause,
  Save,
  X,
  GripVertical,
  Clock,
  Mail,
  Share2,
  FileText,
  Users,
  BarChart3,
  ChevronDown,
  Eye,
  Edit,
  Trash2
} from 'lucide-react';
import { BlueprintCard } from '@/components/ui/BlueprintCard';
import { BlueprintButton } from '@/components/ui/BlueprintButton';
import { BlueprintBadge } from '@/components/ui/BlueprintBadge';
import { MoveType, MoveConfig } from '@/types/campaign';
import { allMoves, getMovesByType } from '@/data/moveLibrary';
import { cn } from '@/lib/utils';

interface MoveComposerProps {
  onSave?: (moves: MoveConfig[]) => void;
  initialMoves?: MoveConfig[];
  readOnly?: boolean;
}

interface ComposerMove {
  id: string;
  type: MoveType;
  name: string;
  config: MoveConfig;
  delay?: number;
  enabled: boolean;
}

const moveTypeIcons = {
  [MoveType.EMAIL]: Mail,
  [MoveType.SOCIAL_MEDIA]: Share2,
  [MoveType.CONTENT]: FileText,
  [MoveType.OUTREACH]: Users,
  [MoveType.ADS]: BarChart3,
  [MoveType.WEBINAR]: Play,
  [MoveType.LANDING_PAGE]: FileText,
  [MoveType.SMS]: Mail,
  [MoveType.PUSH]: Mail,
  [MoveType.ANALYTICS]: BarChart3
};

const moveTypeColors = {
  [MoveType.EMAIL]: 'bg-[var(--blueprint-light)] text-[var(--blueprint)] border-[var(--blueprint)]/30',
  [MoveType.SOCIAL_MEDIA]: 'bg-[var(--accent-light)] text-[var(--accent)] border-[var(--accent)]/30',
  [MoveType.CONTENT]: 'bg-[var(--success-light)] text-[var(--success)] border-[var(--success)]/30',
  [MoveType.OUTREACH]: 'bg-[var(--warning-light)] text-[var(--warning)] border-[var(--warning)]/30',
  [MoveType.ADS]: 'bg-[var(--error-light)] text-[var(--error)] border-[var(--error)]/30',
  [MoveType.WEBINAR]: 'bg-[var(--blueprint-light)] text-[var(--blueprint)] border-[var(--blueprint)]/30',
  [MoveType.LANDING_PAGE]: 'bg-[var(--accent-light)] text-[var(--accent)] border-[var(--accent)]/30',
  [MoveType.SMS]: 'bg-[var(--warning-light)] text-[var(--warning)] border-[var(--warning)]/30',
  [MoveType.PUSH]: 'bg-[var(--surface)] text-[var(--secondary)] border-[var(--border)]',
  [MoveType.ANALYTICS]: 'bg-[var(--success-light)] text-[var(--success)] border-[var(--success)]/30'
};

export function MoveComposer({ onSave, initialMoves = [], readOnly = false }: MoveComposerProps) {
  const [moves, setMoves] = useState<ComposerMove[]>(
    initialMoves.map((config, index) => ({
      id: `move-${index}`,
      type: MoveType.EMAIL, // Default, should be extracted from config
      name: 'Custom Move',
      config,
      delay: index * 24, // 24 hours between moves
      enabled: true
    }))
  );

  const [selectedMoveType, setSelectedMoveType] = useState<MoveType | null>(null);
  const [showMoveLibrary, setShowMoveLibrary] = useState(false);
  const [editingMove, setEditingMove] = useState<string | null>(null);
  const [previewMode, setPreviewMode] = useState(false);

  // Handle drag and drop
  const handleDragEnd = useCallback((result: DropResult) => {
    if (!result.destination || readOnly) return;

    const items = Array.from(moves);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);

    setMoves(items);
  }, [moves, readOnly]);

  // Add new move
  const addMove = useCallback((template: any) => {
    const newMove: ComposerMove = {
      id: `move-${Date.now()}`,
      type: template.type,
      name: template.name,
      config: template.config,
      delay: moves.length * 24,
      enabled: true
    };

    setMoves(prev => [...prev, newMove]);
    setShowMoveLibrary(false);
  }, [moves.length]);

  // Update move
  const updateMove = useCallback((id: string, updates: Partial<ComposerMove>) => {
    setMoves(prev => prev.map(move =>
      move.id === id ? { ...move, ...updates } : move
    ));
  }, []);

  // Delete move
  const deleteMove = useCallback((id: string) => {
    setMoves(prev => prev.filter(move => move.id !== id));
  }, []);

  // Toggle move enabled
  const toggleMove = useCallback((id: string) => {
    setMoves(prev => prev.map(move =>
      move.id === id ? { ...move, enabled: !move.enabled } : move
    ));
  }, []);

  // Save moves
  const handleSave = useCallback(() => {
    const moveConfigs = moves.map(move => move.config);
    onSave?.(moveConfigs);
  }, [moves, onSave]);

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-[var(--structure-subtle)]">
        <div>
          <h2 className="text-lg font-semibold text-[var(--ink)]">Move Composer</h2>
          <p className="text-sm text-[var(--ink-muted)]">
            Build your campaign sequence with moves
          </p>
        </div>

        <div className="flex items-center gap-2">
          <BlueprintButton
            variant="secondary"
            size="sm"
            onClick={() => setPreviewMode(!previewMode)}
            className="flex items-center gap-2"
          >
            <Eye size={16} />
            {previewMode ? 'Edit' : 'Preview'}
          </BlueprintButton>

          {!readOnly && (
            <>
              <BlueprintButton
                variant="secondary"
                size="sm"
                onClick={() => setShowMoveLibrary(true)}
                className="flex items-center gap-2"
              >
                <Plus size={16} />
                Add Move
              </BlueprintButton>

              <BlueprintButton
                size="sm"
                onClick={handleSave}
                className="flex items-center gap-2"
              >
                <Save size={16} />
                Save
              </BlueprintButton>
            </>
          )}
        </div>
      </div>

      {/* Move Library Sidebar */}
      {showMoveLibrary && (
        <div className="absolute right-0 top-0 bottom-0 w-80 bg-[var(--paper)] border-l border-[var(--structure-subtle)] z-10 overflow-y-auto">
          <div className="p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-[var(--ink)]">Move Library</h3>
              <button
                onClick={() => setShowMoveLibrary(false)}
                className="p-1 hover:bg-[var(--surface)] rounded text-[var(--ink-muted)]"
              >
                <X size={16} />
              </button>
            </div>

            {/* Move Type Filter */}
            <div className="mb-4">
              <select
                value={selectedMoveType || ''}
                onChange={(e) => setSelectedMoveType(e.target.value as MoveType)}
                className="w-full px-3 py-2 text-sm bg-[var(--surface)] border border-[var(--structure-subtle)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)]"
              >
                <option value="">All Types</option>
                {Object.values(MoveType).map(type => (
                  <option key={type} value={type}>
                    {type.replace('_', ' ').charAt(0).toUpperCase() + type.replace('_', ' ').slice(1)}
                  </option>
                ))}
              </select>
            </div>

            {/* Move List */}
            <div className="space-y-2">
              {(selectedMoveType ? getMovesByType(selectedMoveType) : allMoves).map(move => (
                <BlueprintCard
                  key={move.id}
                  className="p-3 cursor-pointer hover:border-[var(--blueprint)] transition-colors"
                  onClick={() => addMove(move)}
                >
                  <div className="flex items-start gap-3">
                    <div className="text-2xl">{move.icon}</div>
                    <div className="flex-1 min-w-0">
                      <h4 className="text-sm font-medium text-[var(--ink)] truncate">
                        {move.name}
                      </h4>
                      <p className="text-xs text-[var(--ink-muted)] mt-1 line-clamp-2">
                        {move.description}
                      </p>
                      <div className="flex items-center gap-2 mt-2">
                        <BlueprintBadge variant="blueprint" size="sm" className={moveTypeColors[move.type]}>
                          {move.type.replace('_', ' ')}
                        </BlueprintBadge>
                        <span className="text-xs text-[var(--ink-ghost)]">
                          {move.difficulty}
                        </span>
                      </div>
                    </div>
                  </div>
                </BlueprintCard>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Move Sequence */}
      <div className="flex-1 overflow-y-auto p-4">
        {moves.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 rounded-full border border-[var(--structure-subtle)] flex items-center justify-center mb-4">
              <Plus size={24} className="text-[var(--ink-ghost)]" />
            </div>
            <h3 className="text-lg font-semibold text-[var(--ink)] mb-2">No moves yet</h3>
            <p className="text-sm text-[var(--ink-muted)] mb-4">
              Add moves to build your campaign sequence
            </p>
            <BlueprintButton onClick={() => setShowMoveLibrary(true)}>
              Add Your First Move
            </BlueprintButton>
          </div>
        ) : (
          <DragDropContext onDragEnd={handleDragEnd}>
            <Droppable droppableId="moves">
              {(provided: DroppableProvided) => (
                <div
                  {...provided.droppableProps}
                  ref={provided.innerRef}
                  className="space-y-3"
                >
                  {moves.map((move, index) => {
                    const Icon = moveTypeIcons[move.type];
                    const isEditing = editingMove === move.id;

                    return (
                      <Draggable
                        key={move.id}
                        draggableId={move.id}
                        index={index}
                        isDragDisabled={readOnly}
                      >
                        {(provided: DraggableProvided, snapshot: DraggableStateSnapshot) => (
                          <BlueprintCard
                            ref={provided.innerRef}
                            {...provided.draggableProps}
                            className={cn(
                              "p-4 transition-all",
                              snapshot.isDragging && "shadow-lg scale-105",
                              !move.enabled && "opacity-50",
                              previewMode && "cursor-default"
                            )}
                          >
                            <div className="flex items-start gap-4">
                              {/* Drag Handle */}
                              {!readOnly && !previewMode && (
                                <div
                                  {...provided.dragHandleProps}
                                  className="mt-1 text-[var(--ink-ghost)] hover:text-[var(--ink)]"
                                >
                                  <GripVertical size={16} />
                                </div>
                              )}

                              {/* Move Icon */}
                              <div className={cn(
                                "p-2 rounded-lg border",
                                moveTypeColors[move.type]
                              )}>
                                <Icon size={20} />
                              </div>

                              {/* Move Details */}
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 mb-1">

                                  <h3 className="text-sm font-semibold text-[var(--ink)]">
                                    {move.name}
                                  </h3>
                                  <BlueprintBadge variant="blueprint" size="sm">
                                    {move.type.replace('_', ' ')}
                                  </BlueprintBadge>
                                  {move.delay && (
                                    <BlueprintBadge variant="default" size="sm" className="flex items-center gap-1">
                                      <Clock size={12} />
                                      {move.delay}h
                                    </BlueprintBadge>
                                  )}
                                </div>

                                {/* Move Configuration Preview */}
                                {!isEditing && (
                                  <div className="text-xs text-[var(--ink-muted)] space-y-1">
                                    {move.config.subject && (
                                      <p>Subject: {move.config.subject}</p>
                                    )}
                                    {move.config.platform && (
                                      <p>Platform: {move.config.platform}</p>
                                    )}
                                    {move.config.contentType && (
                                      <p>Type: {move.config.contentType}</p>
                                    )}
                                  </div>
                                )}

                                {/* Edit Form */}
                                {isEditing && (
                                  <div className="mt-3 space-y-2">
                                    <input
                                      type="text"
                                      value={move.name}
                                      onChange={(e) => updateMove(move.id, { name: e.target.value })}
                                      className="w-full px-2 py-1 text-xs bg-[var(--surface)] border border-[var(--structure-subtle)] rounded focus:outline-none focus:border-[var(--blueprint)]"
                                    />
                                    <div className="flex items-center gap-2">
                                      <label className="text-xs text-[var(--ink-muted)]">Delay (hours):</label>
                                      <input
                                        type="number"
                                        value={move.delay || 0}
                                        onChange={(e) => updateMove(move.id, { delay: parseInt(e.target.value) || 0 })}
                                        className="w-20 px-2 py-1 text-xs bg-[var(--surface)] border border-[var(--structure-subtle)] rounded focus:outline-none focus:border-[var(--blueprint)]"
                                      />
                                    </div>
                                  </div>
                                )}
                              </div>

                              {/* Actions */}
                              {!readOnly && !previewMode && (
                                <div className="flex items-center gap-1">
                                  <button
                                    onClick={() => toggleMove(move.id)}
                                    className={cn(
                                      "p-1.5 rounded transition-colors",
                                      move.enabled
                                        ? "text-[var(--success)] hover:bg-[var(--success-light)]/10"
                                        : "text-[var(--ink-muted)] hover:bg-[var(--surface)]"
                                    )}
                                  >
                                    {move.enabled ? <Pause size={14} /> : <Play size={14} />}
                                  </button>

                                  <button
                                    onClick={() => setEditingMove(isEditing ? null : move.id)}
                                    className="p-1.5 text-[var(--ink-muted)] hover:bg-[var(--surface)] rounded transition-colors"
                                  >
                                    {isEditing ? <Save size={14} /> : <Edit size={14} />}
                                  </button>

                                  <button
                                    onClick={() => deleteMove(move.id)}
                                    className="p-1.5 text-[var(--destructive)] hover:bg-[var(--destructive-light)]/10 rounded transition-colors"
                                  >
                                    <Trash2 size={14} />
                                  </button>
                                </div>
                              )}
                            </div>
                          </BlueprintCard>
                        )}
                      </Draggable>
                    );
                  })}
                  {provided.placeholder}
                </div>
              )}
            </Droppable>
          </DragDropContext>
        )}

        {/* Timeline View */}
        {moves.length > 0 && previewMode && (
          <div className="mt-6 p-4 bg-[var(--surface)] rounded-[var(--radius)]">
            <h3 className="text-sm font-semibold text-[var(--ink)] mb-3">Campaign Timeline</h3>
            <div className="space-y-2">
              {moves.map((move, index) => {
                const startTime = moves.slice(0, index).reduce((acc, m) => acc + (m.delay || 0), 0);
                const Icon = moveTypeIcons[move.type];

                return (
                  <div key={move.id} className="flex items-center gap-3 text-xs">
                    <div className="w-8 text-right text-[var(--ink-muted)]">
                      Day {Math.floor(startTime / 24)}
                    </div>
                    <div className={cn(
                      "p-1 rounded",
                      moveTypeColors[move.type]
                    )}>
                      <Icon size={12} />
                    </div>
                    <span className={cn(
                      "flex-1",
                      !move.enabled && "text-[var(--ink-ghost)]"
                    )}>
                      {move.name}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
