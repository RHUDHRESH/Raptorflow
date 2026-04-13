# RAPTORFLOW ADDENDUM C: THE OFFICE TECHNICAL SPECIFICATION

This addendum fills the critical gaps identified in RedTeam Audit Hole 3.

---

## 3A — Technology Choice and Rendering Architecture

### Technology Stack

```typescript
// The Office uses a layered rendering architecture:

// Layer 1: SVG-based character rendering
// - Each character is an SVG with articulated parts (head, body, arms)
// - CSS transforms for positioning and basic animations
// - Framer Motion for complex animations and transitions

// Layer 2: PixiJS for high-performance canvas rendering (optional for complex scenes)
// - Used for scenes with many concurrent animations
// - Particle effects, complex transitions

// Layer 3: DOM overlay for UI elements
// - Speech bubbles
// - Tooltips
// - Interactive elements

// Primary: Next.js + React + Framer Motion + SVG
// The Office is NOT a game engine — it's an animated SVG illustration system
```

### Rendering Architecture

```typescript
// packages/office/src/Office.tsx
import { useReducer, createContext, useContext } from 'react';
import { Canvas } from './components/Canvas';
import { CharacterLayer } from './components/CharacterLayer';
import { OfficeMap } from './components/OfficeMap';
import { UILayer } from './components/UILayer';

interface OfficeState {
  characters: Map<string, CharacterState>;
  animations: AnimationQueue;
  viewport: ViewportState;
  mode: 'passive' | 'active';
}

export function Office({ sessionId, orgId }: OfficeProps) {
  const [state, dispatch] = useReducer(officeReducer, initialState);

  // WebSocket connection for real-time events
  const socket = useRaptorSocket(orgId);

  // Handle incoming office events
  useEffect(() => {
    socket.on('office.event', (event: OfficeEvent) => {
      dispatch({ type: 'OFFICE_EVENT', payload: event });
    });
    return () => socket.off('office.event');
  }, [socket]);

  return (
    <OfficeContext.Provider value={{ state, dispatch }}>
      <Canvas>
        <OfficeMap />
        <CharacterLayer characters={state.characters} />
        <UILayer />
      </Canvas>
    </OfficeContext.Provider>
  );
}
```

### Zoom and Pan Architecture

```typescript
// packages/office/src/components/Viewport.tsx
import { useRef, useCallback } from "react";
import { Transform, TransformHandle } from "./types";

// pixi-viewport for pan and zoom
import { Viewport } from "pixi-viewport";

interface ViewportState {
  x: number;
  y: number;
  scale: number;
  minScale: number;
  maxScale: number;
}

export function useViewport() {
  const viewportRef = useRef<Viewport | null>(null);

  const zoomTo = useCallback((target: string, scale: number = 1.5) => {
    // Find character or location
    const position = getPosition(target);

    viewportRef.current?.animate({
      x: position.x,
      y: position.y,
      scale,
      duration: 500,
      ease: "ease-out",
    });
  }, []);

  const panTo = useCallback((x: number, y: number) => {
    viewportRef.current?.animate({
      x,
      y,
      duration: 300,
    });
  }, []);

  return { viewportRef, zoomTo, panTo };
}

// Zoom levels:
// 1.0 = Full office view
// 1.5 = Character detail view
// 2.0+ = Close-up on specific element

// Character detail rendering at max zoom:
// - At scale > 1.5, swap to high-detail SVG variant
// - At scale > 2.5, show additional details (facial expression, accessories)
// - Performance: only render high-detail for visible characters
```

---

## 3B — The Animation State Machine

### Character States

```typescript
// packages/office/src/types/CharacterState.ts
export type CharacterState =
  | "idle"
  | "walking"
  | "speaking"
  | "reading"
  | "thinking"
  | "celebrating"
  | "concerned"
  | "alert"
  | "pager_buzz"
  | "at_desk"
  | "in_meeting"
  | "at_whiteboard";

export type AnimationTrigger =
  | { type: "TIMER"; duration: number }
  | { type: "WEBSOCKET_EVENT"; event: OfficeEvent }
  | { type: "INTERACTION"; action: UserAction }
  | { type: "SYSTEM"; event: SystemEvent };

// Animation state machine for each character
// Each character runs its own state machine instance

interface CharacterStateMachine {
  state: CharacterState;
  context: CharacterContext;
  transitions: StateTransition[];
}

const characterStateMachine: CharacterStateMachine = {
  state: "idle",
  transitions: [
    // Idle transitions
    {
      from: "idle",
      to: "walking",
      trigger: { type: "WEBSOCKET_EVENT", event: { type: "agent_walk_to_conference" } },
      action: "beginWalk",
    },
    {
      from: "idle",
      to: "speaking",
      trigger: { type: "WEBSOCKET_EVENT", event: { type: "agent_speaking" } },
      action: "beginSpeak",
    },
    {
      from: "idle",
      to: "pager_buzz",
      trigger: { type: "WEBSOCKET_EVENT", event: { type: "pager_notification" } },
      action: "showPager",
    },

    // Walking transitions
    {
      from: "walking",
      to: "at_meeting",
      trigger: { type: "WEBSOCKET_EVENT", event: { type: "conference_room_debate_start" } },
      action: "arriveAtConference",
    },

    // Speaking transitions
    {
      from: "speaking",
      to: "idle",
      trigger: { type: "TIMER", duration: 3000 },
      action: "endSpeak",
    },

    // Meeting transitions
    {
      from: "at_meeting",
      to: "at_desk",
      trigger: { type: "WEBSOCKET_EVENT", event: { type: "conference_room_break" } },
      action: "returnToDesk",
    },

    // Alert transitions
    {
      from: "*",
      to: "alert",
      trigger: { type: "WEBSOCKET_EVENT", event: { type: "intelligence_alert" } },
      action: "showAlert",
    },
    {
      from: "alert",
      to: "idle",
      trigger: { type: "TIMER", duration: 5000 },
      action: "clearAlert",
    },
  ],
};
```

### Animation System

```typescript
// packages/office/src/systems/AnimationSystem.ts
import { create } from "zustand";
import { motion } from "framer-motion";

interface AnimationConfig {
  idle: AnimationDefinition;
  walking: AnimationDefinition;
  speaking: AnimationDefinition;
  celebrating: AnimationDefinition;
}

const animationConfigs: Record<CharacterState, AnimationConfig> = {
  idle: {
    idle: {
      variant: "breathing",
      duration: 2000,
      repeat: Infinity,
      scale: [1, 1.02, 1],
    },
  },
  speaking: {
    speaking: {
      variant: "lipSync",
      duration: 150,
      repeat: Infinity,
    },
    gesture: {
      variant: "handGesture",
      duration: 800,
      repeat: Infinity,
    },
  },
  walking: {
    locomotion: {
      variant: "walkCycle",
      duration: 600,
      repeat: Infinity,
    },
  },
  celebrating: {
    particle: {
      variant: "confetti",
      duration: 2000,
      repeat: 1,
    },
  },
};

// Framer Motion animations for each state
export const characterAnimations = {
  idle: {
    initial: { opacity: 0.8, scale: 1 },
    animate: {
      opacity: [0.8, 1, 0.8],
      scale: [1, 1.02, 1],
      transition: { duration: 2, repeat: Infinity },
    },
  },
  walking: {
    animate: (targetX: number, targetY: number) => ({
      x: targetX,
      y: targetY,
      transition: { duration: 0.8, ease: "easeInOut" },
    }),
  },
  speaking: {
    initial: { scaleY: 1 },
    animate: {
      scaleY: [1, 1.01, 1],
      transition: { duration: 0.15, repeat: Infinity },
    },
  },
  celebrating: {
    animate: {
      rotate: [0, 10, -10, 0],
      scale: [1, 1.2, 1],
      transition: { duration: 0.5 },
    },
  },
};
```

---

## 3C — The OfficeEvent WebSocket Message Schema

```typescript
// packages/contracts/src/office.ts

export type OfficeEventType =
  | "file_delivery_start"
  | "file_delivery_received_by_maya"
  | "file_delivery_to_office"
  | "brief_accepted"
  | "brief_clarification_needed"
  | "pager_notification"
  | "agent_walk_to_conference"
  | "conference_room_debate_start"
  | "agent_speaking"
  | "synthesis_start"
  | "conference_room_break"
  | "move_completed"
  | "task_missed"
  | "intelligence_alert"
  | "morning_meeting_start"
  | "snark_bubble"
  | "dm_thread_update";

export interface OfficeEvent {
  event_type: OfficeEventType;
  agent_id?: string;
  from_agent_id?: string;
  to_agent_id?: string;
  file_name?: string;
  duration_ms?: number;
  session_id?: string;
  timestamp: string;
  metadata?: Record<string, unknown>;
}

// Event to animation mapping
export function mapEventToAnimation(event: OfficeEvent): AnimationTrigger {
  switch (event.event_type) {
    case "file_delivery_start":
      return {
        type: "WEBSOCKET_EVENT",
        event: {
          from: "maya",
          to: event.to_agent_id!,
          animation: "fileCarry",
        },
      };
    case "pager_notification":
      return {
        type: "WEBSOCKET_EVENT",
        event: {
          character: event.agent_id!,
          animation: "pagerBuzz",
        },
      };
    case "agent_walk_to_conference":
      return {
        type: "WEBSOCKET_EVENT",
        event: {
          character: event.agent_id!,
          destination: "conference_room",
          animation: "walk",
        },
      };
    case "conference_room_debate_start":
      return {
        type: "WEBSOCKET_EVENT",
        event: {
          characters: event.metadata?.participants,
          animation: "sitAtTable",
        },
      };
    case "agent_speaking":
      return {
        type: "WEBSOCKET_EVENT",
        event: {
          character: event.agent_id!,
          animation: "speak",
          duration: event.duration_ms,
        },
      };
    case "synthesis_start":
      return {
        type: "WEBSOCKET_EVENT",
        event: {
          character: "strategist",
          animation: "typing",
        },
      };
    case "intelligence_alert":
      return {
        type: "WEBSOCKET_EVENT",
        event: {
          character: event.agent_id!,
          animation: "alert",
        },
      };
    case "snark_bubble":
      return {
        type: "WEBSOCKET_EVENT",
        event: {
          character: event.agent_id!,
          bubbleType: "snark",
          text: event.metadata?.text,
        },
      };
    default:
      return { type: "TIMER", duration: 0 };
  }
}
```

### Event Flow Example

```typescript
// Example: Brief Accepted Event Flow

// 1. Backend sends WebSocket event
const event: OfficeEvent = {
  event_type: "brief_accepted",
  agent_id: "strategist",
  timestamp: new Date().toISOString(),
  metadata: {
    brief_id: "brief_123",
    campaign_name: "Spring Launch",
  },
};

// 2. Frontend receives event
socket.on("office.event", (event: OfficeEvent) => {
  if (event.event_type === "brief_accepted") {
    // 3. Animation system processes event
    const trigger = mapEventToAnimation(event);
    animationEngine.dispatch(trigger);

    // 4. Character state machine transitions
    characterStates.get("strategist")?.transition("celebrating");

    // 5. Office map updates
    officeMap.showCelebration();
  }
});

// 3. Animation plays
// Strategist: brief_accepted → celebrating → idle
// Snark bubble: "Brief accepted. Maya's taking notes. Finally."
```

---

## 3D — Snark Batch Output Format and Storage

```typescript
// packages/contracts/src/snark.ts

export interface SnarkBatch {
  batch_id: string;
  generated_at: string;
  office_chat_messages: OfficeChatMessage[];
  dm_threads: DMThread[];
  speech_bubbles: SpeechBubble[];
}

export interface OfficeChatMessage {
  message_id: string;
  agent_id: string;
  text: string;
  timestamp: string;
  channel: "general" | "campaign" | "intel";
}

export interface DMThread {
  thread_id: string;
  participants: [string, string];
  messages: {
    from: string;
    text: string;
    timestamp: string;
  }[];
}

export interface SpeechBubble {
  bubble_id: string;
  agent_id: string;
  text: string;
  trigger: SpeechBubbleTrigger;
  trigger_condition?: string;
  display_duration_ms: number;
  valid_from: string;
  valid_until: string;
  priority: "low" | "normal" | "high";
}

export type SpeechBubbleTrigger =
  | "idle"
  | "post_debate"
  | "post_task_complete"
  | "scheduled"
  | "event";

export interface SnarkTriggerCondition {
  type: "last_debate_loser" | "campaign_at_risk" | "competitor_move" | "task_streak";
  operator: "equals" | "contains" | "gt";
  value: string | number;
}

// Snark generation prompt
export const SNARK_GENERATION_PROMPT = `You are generating office banter for the RaptorFlow AI office.
// Generate 3-5 speech bubbles for characters who are idle.
// Rules:
// - Snark should be witty, not mean
// - Reference ongoing campaigns or recent events
// - Character voice must be distinct
// - Nothing that reveals system internals
// - No political content, no religion, no sensitive topics

Output JSON:
{
  "speech_bubbles": [
    {
      "agent_id": "ogilvy",
      "text": "Text of bubble",
      "trigger": "idle",
      "display_duration_ms": 5000
    }
  ]
}`;
```

### Snark Display Logic

```typescript
// packages/office/src/systems/SnarkSystem.ts

export function useSnarkBubbles(validBubbles: SpeechBubble[]) {
  const [activeBubble, setActiveBubble] = useState<SpeechBubble | null>(null);
  const { state } = useOfficeContext();

  // Filter bubbles based on current state
  const eligibleBubbles = validBubbles.filter((bubble) => {
    // Check time validity
    const now = new Date();
    const validFrom = new Date(bubble.valid_from);
    const validUntil = new Date(bubble.valid_until);
    if (now < validFrom || now > validUntil) return false;

    // Check trigger conditions
    if (bubble.trigger_condition) {
      return evaluateCondition(bubble.trigger_condition, state);
    }

    return (
      bubble.trigger === "idle" ||
      (bubble.trigger === "event" && matchesCurrentEvent(bubble, state))
    );
  });

  // Display bubbles on timer
  useEffect(() => {
    if (eligibleBubbles.length === 0) return;

    const bubble = eligibleBubbles[Math.floor(Math.random() * eligibleBubbles.length)];
    setActiveBubble(bubble);

    const timer = setTimeout(() => {
      setActiveBubble(null);
    }, bubble.display_duration_ms);

    return () => clearTimeout(timer);
  }, [eligibleBubbles]);

  return activeBubble;
}
```

---

## 3E — Passive vs Active Mode (Technical Difference)

```typescript
// Passive mode: Office animates without user interaction
// Active mode: User is interacting with office elements

export type OfficeMode = "passive" | "active";

export function useOfficeMode(): OfficeMode {
  const [mode, setMode] = useState<OfficeMode>("passive");
  const viewportRef = useViewportRef();

  useEffect(() => {
    // Switch to active mode when user interacts
    const handleInteraction = () => {
      if (mode === "passive") {
        setMode("active");
      }
    };

    // Switch back to passive after 30 seconds of no interaction
    let idleTimer: NodeJS.Timeout;

    const resetIdleTimer = () => {
      clearTimeout(idleTimer);
      idleTimer = setTimeout(() => {
        setMode("passive");
      }, 30000);
    };

    document.addEventListener("mousemove", handleInteraction);
    document.addEventListener("click", handleInteraction);
    document.addEventListener("scroll", handleInteraction);

    const viewport = viewportRef.current;
    viewport?.on("mouseover", handleInteraction);

    return () => {
      document.removeEventListener("mousemove", handleInteraction);
      document.removeEventListener("click", handleInteraction);
      document.removeEventListener("scroll", handleInteraction);
      viewport?.off("mouseover", handleInteraction);
      clearTimeout(idleTimer);
    };
  }, [mode]);

  return mode;
}

// Passive mode optimizations:
// - Reduce animation frame rate to 30fps
// - Pause particle effects
// - Disable hover interactions
// - Batch WebSocket event processing
// - Reduce character detail level

// Active mode:
// - Full 60fps animation
// - All effects enabled
// - Full interaction support
// - Real-time event processing
```

---

## Summary

This addendum provides:

1. **Technology choice** — SVG + Framer Motion + React, not a game engine
2. **Rendering architecture** — layered system with Canvas, Character, and UI layers
3. **Zoom and pan architecture** — pixi-viewport with level-of-detail rendering
4. **Animation state machine** — complete state definitions and transition rules
5. **OfficeEvent WebSocket schema** — all event types with TypeScript definitions
6. **Snark batch format** — complete schema and trigger conditions
7. **Passive vs Active mode** — technical implementation difference

These specifications complete the Office animation gap identified in RedTeam Audit Hole 3.
