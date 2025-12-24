# RaptorFlow — DESIGN GATE (Ship/No-Ship)

This is a merge-blocking checklist for every new screen.
If any **NO** in sections 1–3 → do not ship.

---

## 1) Purpose Gate (Must be YES)

- [ ] This screen has **one** primary job.
- [ ] There is **one** primary CTA.
- [ ] A first-time user understands the job in **5 seconds**.
- [ ] Everything on this screen changes a decision or enables the CTA.
- [ ] If I remove 50% of elements, the purpose is still clear.

**Primary job:** ______________________
**Primary CTA:** ______________________
**Next screen after CTA:** ______________________

---

## 2) Layout Gate (Must be YES)

- [ ] Page padding ≥ **48px** (desktop), ≥ **24px** (mobile).
- [ ] Section spacing ≥ **48px**.
- [ ] Content width constrained (max **1000–1200px**).
- [ ] Single column by default; multi-column only if necessary.
- [ ] Above-the-fold contains: title + context + CTA.

---

## 3) Typography Gate (Must be YES)

- [ ] Page title uses **Playfair Display** only.
- [ ] All other text uses **Inter**.
- [ ] Numbers/metrics use **JetBrains Mono**.
- [ ] Body text is **16px** with 1.5+ line height.
- [ ] Type weights limited to **400 / 500 / 600**.
- [ ] Hierarchy still reads correctly in grayscale.

---

## 4) Color Gate (Strongly preferred)

- [ ] 90%+ neutral UI.
- [ ] No colored card backgrounds.
- [ ] No colored borders.
- [ ] Accent used ≤10% total area (or not at all).
- [ ] Canvas is slightly warm (not pure white).
- [ ] WCAG AA contrast passes.

---

## 5) Components Gate

- [ ] Primary button: solid ink (#171717) with white text.
- [ ] Secondary buttons: outline-only.
- [ ] Ghost: text/underline on hover.
- [ ] Button height 44–48px, radius 12–14px.
- [ ] Inputs minimal, height 48–56px.
- [ ] Cards: minimal border OR ultra-subtle shadow (not both everywhere).

---

## 6) Motion Gate

- [ ] Animations ≤220–300ms.
- [ ] Ease-out only. No bounce.
- [ ] Movement distance 8–16px max.
- [ ] No scroll entrance animation.
- [ ] No gamification/confetti.

---

## 7) Content Gate

- [ ] ≤4 metrics visible at once.
- [ ] Charts exist only if they change a decision.
- [ ] Complex data is behind "View more".
- [ ] Copy can't be cut in half without losing meaning.
- [ ] Empty states give one clear action.

---

## 8) Navigation Gate

- [ ] Sidebar ≤10 items.
- [ ] Current location is obvious.
- [ ] Home reachable in one click.
- [ ] Navigation fades into background (not competing with content).

---

## Final Test (Must be YES)

- [ ] Would Apple ship this layout?
- [ ] Does it feel as restrained as MasterClass?
- [ ] Is the UI as invisible as ChatGPT?

If any NO → simplify and resubmit.

---

## 12 Non-Negotiable Heuristics

### A) Purpose & Hierarchy
1. **One screen = one job.** If it has 2 jobs, split it.
2. **One primary CTA, always.** Everything else is subordinate.
3. **If it doesn't change a decision, delete it.**

### B) Layout & Density
4. **Whitespace is a feature.** 48px edges, 48px section gaps.
5. **Single column by default.** Multi-column only when comparing things.
6. **Above-the-fold must contain the action + context.**

### C) Type & Color
7. **One serif headline. Everything else Inter.**
8. **Neutral-only.** No colored surfaces, no colored borders.
9. **Monochrome hierarchy must work blurred (squint test).**

### D) Components & Motion
10. **Borders over shadows.** Shadows only for active elevation.
11. **No "cute UI."** No pills, no badges everywhere, no gamification.
12. **Motion is invisible.** ≤220ms, ease-out, small distance.
