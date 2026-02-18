# src/components/ - UI Component Library

**Parent:** `src/AGENTS.md`

## OVERVIEW
Large React component library with 20+ subdirectories covering UI primitives, domain components, and feature-specific modules.

## STRUCTURE
```
src/components/
├── AgentChat.tsx          # Main AI chat interface
├── AgentManagement.tsx    # AI agent management
├── WorkflowBuilder.tsx    # Campaign workflow builder
├── ui/                   # Base UI primitives (Button, Card, Input)
├── dashboard/            # Dashboard-specific components
├── workspace/            # Workspace components
├── landing/              # Landing page components
├── animation/            # GSAP animations
├── providers/            # React context providers
└── [20+ more subdirs]   # Feature-specific components
```

## WHERE TO LOOK
| Component | File | Purpose |
|-----------|------|---------|
| AI Chat | `AgentChat.tsx` | Main chat interface |
| Workflow Builder | `WorkflowBuilder.tsx` | Campaign workflow editor |
| UI primitives | `ui/` | Button, Card, Input components |
| Dashboard | `dashboard/` | Stats, charts, widgets |

## CONVENTIONS
- Complex components: `.tsx` with TypeScript
- Simple components: `.jsx`
- Use Tailwind CSS for styling
- Framer Motion for animations
- CVA (class-variance-authority) for variant props

## ANTI-PATTERNS
- NO inline styles - use Tailwind
- NO large monolithic components - extract
- NO direct Supabase calls - use hooks/stores
