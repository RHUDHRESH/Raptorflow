declare module 'react-big-calendar' {
    import { ComponentType, Component } from 'react';

    export type View = 'month' | 'week' | 'work_week' | 'day' | 'agenda';

    export interface Views {
        MONTH: 'month';
        WEEK: 'week';
        WORK_WEEK: 'work_week';
        DAY: 'day';
        AGENDA: 'agenda';
    }
    export const Views: Views;

    export interface CalendarProps<TEvent extends object = Event, TResource extends object = object> {
        localizer: any;
        events?: TEvent[];
        startAccessor?: string | ((event: TEvent) => Date);
        endAccessor?: string | ((event: TEvent) => Date);
        view?: View;
        date?: Date;
        onNavigate?: (newDate: Date, view: View, action: string) => void;
        onView?: (view: View) => void;
        onSelectEvent?: (event: TEvent, e: React.SyntheticEvent<HTMLElement>) => void;
        onSelectSlot?: (slotInfo: {
            start: Date;
            end: Date;
            slots: Date[];
            action: 'select' | 'click' | 'doubleClick';
        }) => void;
        selectable?: boolean | 'ignoreEvents';
        eventPropGetter?: (event: TEvent, start: Date, end: Date, isSelected: boolean) => { className?: string; style?: React.CSSProperties };
        components?: any;
        style?: React.CSSProperties;
    }

    export class Calendar<TEvent extends object = Event, TResource extends object = object> extends Component<CalendarProps<TEvent, TResource>> { }

    export function dateFnsLocalizer(config: {
        format: any;
        parse: any;
        startOfWeek: any;
        getDay: any;
        locales: any;
    }): any;
}
