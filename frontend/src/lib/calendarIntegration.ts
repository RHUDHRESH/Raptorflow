// Google Calendar API integration utilities
// Note: This is a simplified implementation. In production, you'll need proper OAuth setup

export interface CalendarEvent {
  id: string;
  title: string;
  start: Date;
  end: Date;
  description?: string;
  location?: string;
}

export interface GoogleCalendarConfig {
  clientId: string;
  apiKey: string;
  scopes: string[];
}

// Load Google Calendar API
export const loadGoogleCalendarAPI = (): Promise<void> => {
  return new Promise((resolve, reject) => {
    if ((window as any).gapi?.calendar) {
      resolve();
      return;
    }

    const script = document.createElement('script');
    script.src = 'https://apis.google.com/js/api.js';
    script.onload = () => {
      (window as any).gapi.load('client:auth2', () => {
        (window as any).gapi.client.init({
          apiKey: process.env.NEXT_PUBLIC_GOOGLE_API_KEY,
          clientId: process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID,
          discoveryDocs: ['https://www.googleapis.com/discovery/v1/apis/calendar/v3/rest'],
          scope: 'https://www.googleapis.com/auth/calendar.events'
        }).then(() => {
          resolve();
        }).catch(reject);
      });
    };
    script.onerror = reject;
    document.head.appendChild(script);
  });
};

// Authenticate with Google
export const authenticateGoogle = async (): Promise<boolean> => {
  try {
    await loadGoogleCalendarAPI();
    const GoogleAuth = (window as any).gapi.auth2.getAuthInstance();
    const user = await GoogleAuth.signIn();
    return user.isSignedIn();
  } catch (error) {
    console.error('Google authentication failed:', error);
    return false;
  }
};

// Get calendar events
export const getCalendarEvents = async (calendarId: string = 'primary', timeMin?: Date, timeMax?: Date): Promise<CalendarEvent[]> => {
  try {
    const response = await (window as any).gapi.client.calendar.events.list({
      calendarId,
      timeMin: timeMin?.toISOString(),
      timeMax: timeMax?.toISOString(),
      singleEvents: true,
      orderBy: 'startTime'
    });

    return response.result.items.map((item: any) => ({
      id: item.id,
      title: item.summary,
      start: new Date(item.start.dateTime || item.start.date),
      end: new Date(item.end.dateTime || item.end.date),
      description: item.description,
      location: item.location
    }));
  } catch (error) {
    console.error('Failed to fetch calendar events:', error);
    return [];
  }
};

// Create calendar event
export const createCalendarEvent = async (event: Omit<CalendarEvent, 'id'>, calendarId: string = 'primary'): Promise<string | null> => {
  try {
    const response = await (window as any).gapi.client.calendar.events.insert({
      calendarId,
      resource: {
        summary: event.title,
        description: event.description,
        location: event.location,
        start: {
          dateTime: event.start.toISOString(),
          timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone
        },
        end: {
          dateTime: event.end.toISOString(),
          timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone
        }
      }
    });

    return response.result.id;
  } catch (error) {
    console.error('Failed to create calendar event:', error);
    return null;
  }
};

// Update calendar event
export const updateCalendarEvent = async (eventId: string, event: Partial<CalendarEvent>, calendarId: string = 'primary'): Promise<boolean> => {
  try {
    await (window as any).gapi.client.calendar.events.patch({
      calendarId,
      eventId,
      resource: {
        summary: event.title,
        description: event.description,
        location: event.location,
        ...(event.start && {
          start: {
            dateTime: event.start.toISOString(),
            timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone
          }
        }),
        ...(event.end && {
          end: {
            dateTime: event.end.toISOString(),
            timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone
          }
        })
      }
    });

    return true;
  } catch (error) {
    console.error('Failed to update calendar event:', error);
    return false;
  }
};

// Delete calendar event
export const deleteCalendarEvent = async (eventId: string, calendarId: string = 'primary'): Promise<boolean> => {
  try {
    await (window as any).gapi.client.calendar.events.delete({
      calendarId,
      eventId
    });

    return true;
  } catch (error) {
    console.error('Failed to delete calendar event:', error);
    return false;
  }
};

// Sync Muse assets with Google Calendar
export const syncAssetsWithCalendar = async (assets: any[], calendarId: string = 'primary'): Promise<void> => {
  try {
    // Get existing events
    const existingEvents = await getCalendarEvents(calendarId);
    const existingEventIds = new Set(existingEvents.map(e => e.id));

    // Create events for new assets
    for (const asset of assets) {
      if (!asset.googleCalendarEventId || !existingEventIds.has(asset.googleCalendarEventId)) {
        const eventId = await createCalendarEvent({
          title: asset.title,
          start: new Date(asset.scheduledDate || asset.createdAt),
          end: new Date(new Date(asset.scheduledDate || asset.createdAt).getTime() + 60 * 60 * 1000),
          description: `Content from Muse:\n\n${asset.content.slice(0, 500)}...`
        }, calendarId);

        if (eventId) {
          asset.googleCalendarEventId = eventId;
          // Update asset in your store/database
        }
      }
    }
  } catch (error) {
    console.error('Sync failed:', error);
  }
};

// Check if Google Calendar is available
export const isGoogleCalendarAvailable = (): boolean => {
  return typeof window !== 'undefined' && !!(window as any).gapi;
};

// Mock implementation for development
export const mockCalendarEvents: CalendarEvent[] = [
  {
    id: 'mock-1',
    title: 'Content Planning Meeting',
    start: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000), // 2 days from now
    end: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000 + 60 * 60 * 1000),
    description: 'Plan next month\'s content calendar',
    location: 'Virtual'
  },
  {
    id: 'mock-2',
    title: 'Blog Post Deadline',
    start: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000), // 5 days from now
    end: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000 + 30 * 60 * 1000),
    description: 'Submit Q4 blog post'
  }
];
