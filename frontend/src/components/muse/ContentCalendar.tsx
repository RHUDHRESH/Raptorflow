"use client";

import { useState, useCallback } from 'react';
import { Calendar, dateFnsLocalizer, View, Views } from 'react-big-calendar';
import { format, parse, startOfWeek, getDay } from 'date-fns';
import { enUS } from 'date-fns/locale';
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon, Clock, ExternalLink, RefreshCw } from 'lucide-react';
import { MuseAsset } from '@/stores/museStore';
import { BlueprintCard } from '@/components/ui/BlueprintCard';
import { BlueprintButton } from '@/components/ui/BlueprintButton';
import { cn } from '@/lib/utils';
import { mockCalendarEvents, syncAssetsWithCalendar } from '@/lib/calendarIntegration';

// Setup localizer
const locales = {
  'en-US': enUS,
};
const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek,
  getDay,
  locales,
});

interface CalendarEvent {
  id: string;
  title: string;
  start: Date;
  end: Date;
  allDay?: boolean;
  resource?: {
    asset?: MuseAsset;
    type: 'content' | 'meeting' | 'deadline';
    status: 'scheduled' | 'draft' | 'published';
  };
}

interface ContentCalendarProps {
  assets: MuseAsset[];
  onEventClick?: (event: CalendarEvent) => void;
  onDateSelect?: (date: Date) => void;
}

export function ContentCalendar({ assets, onEventClick, onDateSelect }: ContentCalendarProps) {
  const [view, setView] = useState<View>(Views.MONTH);
  const [date, setDate] = useState(new Date());
  const [selectedEvent, setSelectedEvent] = useState<CalendarEvent | null>(null);
  const [isSyncing, setIsSyncing] = useState(false);
  const [lastSync, setLastSync] = useState<Date | null>(null);

  // Convert assets to calendar events
  const events = useCallback((): CalendarEvent[] => {
    const assetEvents: CalendarEvent[] = assets.map(asset => ({
      id: asset.id,
      title: asset.title,
      start: new Date(asset.createdAt),
      end: new Date(new Date(asset.createdAt).getTime() + 60 * 60 * 1000), // 1 hour duration
      allDay: false,
      resource: {
        asset,
        type: 'content',
        status: asset.tags.includes('Published') ? 'published' : 'draft'
      }
    }));

    // Add some example events
    const today = new Date();
    const exampleEvents: CalendarEvent[] = [
      {
        id: 'meeting-1',
        title: 'Content Planning Meeting',
        start: new Date(today.getFullYear(), today.getMonth(), today.getDate() + 2, 10, 0),
        end: new Date(today.getFullYear(), today.getMonth(), today.getDate() + 2, 11, 0),
        allDay: false,
        resource: {
          type: 'meeting',
          status: 'scheduled'
        }
      },
      {
        id: 'deadline-1',
        title: 'Blog Post Deadline',
        start: new Date(today.getFullYear(), today.getMonth(), today.getDate() + 5, 17, 0),
        end: new Date(today.getFullYear(), today.getMonth(), today.getDate() + 5, 18, 0),
        allDay: false,
        resource: {
          type: 'deadline',
          status: 'scheduled'
        }
      }
    ];

    return [...assetEvents, ...exampleEvents];
  }, [assets]);

  const handleSelectEvent = useCallback((event: CalendarEvent) => {
    setSelectedEvent(event);
    onEventClick?.(event);
  }, [onEventClick]);

  const handleSelectSlot = useCallback(({ start }: { start: Date }) => {
    onDateSelect?.(start);
  }, [onDateSelect]);

  const handleSync = async () => {
    setIsSyncing(true);
    try {
      // In real implementation, this would sync with Google Calendar
      await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate sync
      setLastSync(new Date());
    } catch (error) {
      console.error('Sync failed:', error);
    } finally {
      setIsSyncing(false);
    }
  };

  const navigate = (action: 'PREV' | 'NEXT' | 'TODAY') => {
    if (action === 'PREV') {
      setDate(prev => new Date(prev.getFullYear(), prev.getMonth() - 1, 1));
    } else if (action === 'NEXT') {
      setDate(prev => new Date(prev.getFullYear(), prev.getMonth() + 1, 1));
    } else {
      setDate(new Date());
    }
  };

  const eventStyleGetter = (event: CalendarEvent) => {
    const status = event.resource?.status;
    const type = event.resource?.type;

    let backgroundColor = 'var(--surface)';
    let borderColor = 'var(--structure-subtle)';

    if (type === 'content') {
      if (status === 'published') {
        backgroundColor = 'var(--success-light)';
        borderColor = 'var(--success)';
      } else if (status === 'draft') {
        backgroundColor = 'var(--warning-light)';
        borderColor = 'var(--warning)';
      }
    } else if (type === 'meeting') {
      backgroundColor = 'var(--blueprint-light)';
      borderColor = 'var(--blueprint)';
    } else if (type === 'deadline') {
      backgroundColor = 'var(--destructive-light)';
      borderColor = 'var(--destructive)';
    }

    return {
      style: {
        backgroundColor,
        borderLeft: `4px solid ${borderColor}`,
        borderRadius: '4px',
        padding: '2px 4px',
        fontSize: '12px',
      }
    };
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-[var(--structure-subtle)]">
        <div className="flex items-center gap-4">
          <h2 className="text-lg font-semibold text-[var(--ink)] flex items-center gap-2">
            <CalendarIcon size={20} />
            Content Calendar
          </h2>
          <div className="flex items-center gap-1 text-sm text-[var(--ink-muted)]">
            {format(date, 'MMMM yyyy')}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <BlueprintButton
            variant="secondary"
            size="sm"
            onClick={() => navigate('TODAY')}
          >
            Today
          </BlueprintButton>
          <div className="flex items-center border border-[var(--structure-subtle)] rounded-[var(--radius)]">
            <button
              onClick={() => navigate('PREV')}
              className="p-1 hover:bg-[var(--surface)] rounded-l-[var(--radius)]"
            >
              <ChevronLeft size={16} />
            </button>
            <button
              onClick={() => navigate('NEXT')}
              className="p-1 hover:bg-[var(--surface)] rounded-r-[var(--radius)]"
            >
              <ChevronRight size={16} />
            </button>
          </div>
          <select
            value={view}
            onChange={(e) => setView(e.target.value as View)}
            className="text-sm bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] px-3 py-1.5 focus:outline-none focus:border-[var(--blueprint)]"
          >
            <option value={Views.MONTH}>Month</option>
            <option value={Views.WEEK}>Week</option>
            <option value={Views.DAY}>Day</option>
            <option value={Views.AGENDA}>Agenda</option>
          </select>
        </div>
      </div>

      {/* Calendar */}
      <div className="flex-1 p-4">
        <Calendar
          localizer={localizer}
          events={events()}
          startAccessor="start"
          endAccessor="end"
          view={view}
          date={date}
          onNavigate={setDate}
          onView={setView}
          onSelectEvent={handleSelectEvent}
          onSelectSlot={handleSelectSlot}
          selectable
          eventPropGetter={eventStyleGetter}
          components={{
            toolbar: () => null, // Custom toolbar above
            month: {
              dateHeader: ({ date }: { date: Date }) => (
                <div className="text-xs text-[var(--ink-muted)] uppercase">
                  {format(date, 'EEE')}
                </div>
              ),
            },
          }}
          style={{
            height: '100%',
            backgroundColor: 'var(--paper)',
            borderRadius: 'var(--radius)',
          }}
        />
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-[var(--structure-subtle)]">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4 text-xs">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-[var(--success-light)] border-l-2 border-[var(--success)] rounded"></div>
              <span className="text-[var(--ink-muted)]">Published</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-[var(--warning-light)] border-l-2 border-[var(--warning)] rounded"></div>
              <span className="text-[var(--ink-muted)]">Draft</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-[var(--blueprint-light)] border-l-2 border-[var(--blueprint)] rounded"></div>
              <span className="text-[var(--ink-muted)]">Meeting</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-[var(--destructive-light)] border-l-2 border-[var(--destructive)] rounded"></div>
              <span className="text-[var(--ink-muted)]">Deadline</span>
            </div>
            {lastSync && (
              <span className="text-[var(--ink-ghost)]">
                Last sync: {format(lastSync, 'p')}
              </span>
            )}
          </div>
          <BlueprintButton
            size="sm"
            variant="secondary"
            onClick={handleSync}
            disabled={isSyncing}
            className="flex items-center gap-2"
          >
            <RefreshCw size={14} className={cn(isSyncing && 'animate-spin')} />
            {isSyncing ? 'Syncing...' : 'Sync Calendar'}
          </BlueprintButton>
        </div>
      </div>

      {/* Event Detail Modal */}
      {selectedEvent && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <BlueprintCard className="w-full max-w-md">
            <div className="p-4">
              <div className="flex items-start justify-between mb-4">
                <h3 className="text-lg font-semibold text-[var(--ink)]">
                  {selectedEvent.title}
                </h3>
                <button
                  onClick={() => setSelectedEvent(null)}
                  className="p-1 hover:bg-[var(--surface)] rounded text-[var(--ink-muted)]"
                >
                  ×
                </button>
              </div>

              <div className="space-y-3">
                <div className="flex items-center gap-2 text-sm text-[var(--ink-muted)]">
                  <Clock size={14} />
                  <span>
                    {format(selectedEvent.start, 'PPP p')}
                    {selectedEvent.end && ` - ${format(selectedEvent.end, 'p')}`}
                  </span>
                </div>

                {selectedEvent.resource?.asset && (
                  <div className="p-3 bg-[var(--surface)] rounded-[var(--radius)]">
                    <p className="text-sm text-[var(--ink-muted)] line-clamp-3">
                      {selectedEvent.resource.asset.content.slice(0, 150)}...
                    </p>
                  </div>
                )}

                <div className="flex justify-end gap-2 pt-2">
                  <BlueprintButton
                    variant="secondary"
                    size="sm"
                    onClick={() => setSelectedEvent(null)}
                  >
                    Close
                  </BlueprintButton>
                  {selectedEvent.resource?.asset && (
                    <BlueprintButton size="sm">
                      View Asset
                    </BlueprintButton>
                  )}
                </div>
              </div>
            </div>
          </BlueprintCard>
        </div>
      )}
    </div>
  );
}
