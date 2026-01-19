"use client";

import { useState } from 'react';
import { Calendar, Clock, Send, X } from 'lucide-react';
import { BlueprintCard } from '@/components/ui/BlueprintCard';
import { BlueprintButton } from '@/components/ui/BlueprintButton';
import { MuseAsset } from '@/stores/museStore';
import { cn } from '@/lib/utils';

interface ScheduleContentModalProps {
  asset: MuseAsset | null;
  onClose: () => void;
  onSchedule: (asset: MuseAsset, scheduledDate: Date) => void;
}

export function ScheduleContentModal({ asset, onClose, onSchedule }: ScheduleContentModalProps) {
  const [selectedDate, setSelectedDate] = useState('');
  const [selectedTime, setSelectedTime] = useState('10:00');
  const [notes, setNotes] = useState('');

  if (!asset) return null;

  const handleSchedule = () => {
    if (!selectedDate) return;

    const scheduledDate = new Date(`${selectedDate}T${selectedTime}`);
    onSchedule(asset, scheduledDate);
    onClose();
  };

  const getMinDate = () => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return tomorrow.toISOString().split('T')[0];
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <BlueprintCard className="w-full max-w-md">
        <div className="p-6">
          {/* Header */}
          <div className="flex items-start justify-between mb-4">
            <div>
              <h2 className="text-lg font-semibold text-[var(--ink)] flex items-center gap-2">
                <Calendar size={20} />
                Schedule Content
              </h2>
              <p className="text-sm text-[var(--ink-muted)] mt-1">
                {asset.title}
              </p>
            </div>
            <button
              onClick={onClose}
              className="p-1 hover:bg-[var(--surface)] rounded text-[var(--ink-muted)]"
            >
              <X size={20} />
            </button>
          </div>

          {/* Content Preview */}
          <div className="p-3 bg-[var(--surface)] rounded-[var(--radius)] mb-4">
            <p className="text-sm text-[var(--ink-muted)] line-clamp-3">
              {asset.content.slice(0, 150)}...
            </p>
          </div>

          {/* Schedule Form */}
          <div className="space-y-4">
            {/* Date Selection */}
            <div>
              <label className="block text-sm font-medium text-[var(--ink)] mb-2">
                Date
              </label>
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                min={getMinDate()}
                className="w-full px-3 py-2 text-sm bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)]"
              />
            </div>

            {/* Time Selection */}
            <div>
              <label className="block text-sm font-medium text-[var(--ink)] mb-2">
                Time
              </label>
              <input
                type="time"
                value={selectedTime}
                onChange={(e) => setSelectedTime(e.target.value)}
                className="w-full px-3 py-2 text-sm bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)]"
              />
            </div>

            {/* Notes */}
            <div>
              <label className="block text-sm font-medium text-[var(--ink)] mb-2">
                Notes (optional)
              </label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Add any notes or reminders..."
                rows={3}
                className="w-full px-3 py-2 text-sm bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)] resize-none"
              />
            </div>

            {/* Sync Options */}
            <div className="p-3 bg-[var(--blueprint-light)]/10 rounded-[var(--radius)]">
              <div className="flex items-start gap-2">
                <input
                  type="checkbox"
                  id="sync-google"
                  className="mt-1 rounded border-[var(--structure-subtle)] text-[var(--blueprint)] focus:ring-[var(--blueprint)]"
                  defaultChecked
                />
                <label htmlFor="sync-google" className="text-sm text-[var(--ink)]">
                  <span className="font-medium">Sync to Google Calendar</span>
                  <p className="text-[var(--ink-muted)] mt-1">
                    Automatically add this to your Google Calendar
                  </p>
                </label>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-2 mt-6">
            <BlueprintButton
              variant="secondary"
              onClick={onClose}
            >
              Cancel
            </BlueprintButton>
            <BlueprintButton
              onClick={handleSchedule}
              disabled={!selectedDate}
              className="flex items-center gap-2"
            >
              <Send size={16} />
              Schedule
            </BlueprintButton>
          </div>
        </div>
      </BlueprintCard>
    </div>
  );
}

interface QuickScheduleProps {
  asset: MuseAsset;
  onSchedule: (asset: MuseAsset, date: Date) => void;
}

export function QuickSchedule({ asset, onSchedule }: QuickScheduleProps) {
  const [isOpen, setIsOpen] = useState(false);

  const quickOptions = [
    {
      label: 'Tomorrow Morning',
      getDate: () => {
        const date = new Date();
        date.setDate(date.getDate() + 1);
        date.setHours(9, 0, 0, 0);
        return date;
      }
    },
    {
      label: 'Tomorrow Afternoon',
      getDate: () => {
        const date = new Date();
        date.setDate(date.getDate() + 1);
        date.setHours(14, 0, 0, 0);
        return date;
      }
    },
    {
      label: 'Next Week',
      getDate: () => {
        const date = new Date();
        date.setDate(date.getDate() + 7);
        date.setHours(10, 0, 0, 0);
        return date;
      }
    }
  ];

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-1 text-xs text-[var(--blueprint)] hover:underline"
      >
        <Clock size={12} />
        Schedule
      </button>

      {isOpen && (
        <div className="absolute bottom-full left-0 mb-2 w-48 bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] shadow-lg z-10">
          <div className="p-2">
            {quickOptions.map((option, index) => (
              <button
                key={index}
                onClick={() => {
                  onSchedule(asset, option.getDate());
                  setIsOpen(false);
                }}
                className="w-full text-left px-3 py-2 text-sm text-[var(--ink)] hover:bg-[var(--surface)] rounded-[var(--radius)] transition-colors"
              >
                {option.label}
              </button>
            ))}
            <hr className="my-2 border-[var(--structure-subtle)]" />
            <button
              onClick={() => {
                setIsOpen(false);
                // Open full schedule modal
              }}
              className="w-full text-left px-3 py-2 text-sm text-[var(--blueprint)] hover:bg-[var(--blueprint-light)]/10 rounded-[var(--radius)] transition-colors"
            >
              Custom Date & Time...
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
