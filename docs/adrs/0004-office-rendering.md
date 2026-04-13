# ADR 0004: Office Rendering

## Status

Accepted

## Decision

Render The Office as a PixiJS v8 canvas with a React overlay layer, using `pixi-viewport` for pan and zoom.

## Rationale

- The Office requires many simultaneous animated entities
- Canvas/WebGL fits the event-driven animation model better than DOM or SVG
- React remains responsible for HUD, side panels, speech metadata, and control surfaces
