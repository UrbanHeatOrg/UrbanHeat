# Frontend Design & UI Aesthetics Guidelines

Follow Anthropic's core frontend design principles to avoid generic, "on-distribution" UI patterns (the "AI slop" aesthetic). Build distinctive, bespoke, state-of-the-art interfaces that look like they were crafted by top-tier product designers.

---

## 1. Avoid the "AI Slop" Defaults
- **Do NOT** use default system fonts (Arial, Helvetica, Inter, Roboto).
- **Do NOT** rely on cliché, washed-out purple-on-dark gradients or generic SaaS template cards.
- **Do NOT** generate static, lifeless interfaces with missing hover states or unstyled focus rings.
- **Do NOT** build boxy, flat cards without visual hierarchy, atmospheric depth, or borders.

---

## 2. Typography & Spatial Rhythm
- **Curated Font Pairings**:
  - **Headings & UI**: Clean, expressive modern sans (e.g., *Plus Jakarta Sans*, *Outfit*, *Geist*, *Syne*).
  - **Data, Telemetry & Code**: High-legibility monospaced font (e.g., *JetBrains Mono*, *Fira Code*) for coordinates, FIPS Census IDs, temperature readings, and model outputs.
- **Visual Hierarchy**: Strong typographic scale with high contrast between primary data points (large, bold, prominent) and secondary metadata (subtle, muted, tracking-wide uppercase labels).

---

## 3. Color, Theme & Atmospheric Depth
- **Cohesive Palettes**:
  - Prefer dark command-center / HUD themes with deep slate or obsidian foundations (`#0B0F17`, `#0F172A`).
  - High-contrast, purposeful accent colors (e.g., Emerald `#10B981` for resilience/safe zones, Amber `#F59E0B` for transit alert burdens, Electric Rose/Crimson `#F43F5E` for extreme heat hazards).
- **Depth & Translucency**:
  - Use subtle glassmorphism (`backdrop-blur-md`, `bg-slate-900/80`, `border border-white/10`).
  - Add atmospheric touches like subtle radial glow backgrounds, micro-gridlines, or fine dividers instead of harsh solid boundaries.

---

## 4. Component Primitives & Micro-Interactions
- **Component Architecture**:
  - Favor accessible, headless primitives (Radix UI, React Aria, or shadcn/ui components) styled with utility classes.
  - Keep styling modular and token-driven via CSS variables and Tailwind utility classes.
- **Micro-Interactions & Polish**:
  - Every interactive element (buttons, cards, toggles, filter pills) MUST have active, hover, and focus states (`transition-all duration-200 ease-in-out`).
  - Use live status indicators with soft pulse rings (e.g., `animate-pulse` or radar pings for active sensors/cooling centers).
  - Smooth expansion/collapse transitions for accordions, slide-over sheets, and modals.

---

## 5. Dashboard & Spatial Data Density
- Design for rapid municipal decision-making:
  - Scannable metric cards with trend indicators and sparklines.
  - High data density without clutter (well-proportioned padding, clear groupings, and contextual tooltips).
  - Vector maps with high-contrast layer toggles (buffers, census tracts, heat hazards).
- Verify responsiveness across viewport widths (desktop widescreen, standard laptop, and tablet viewports) using automated headless browser testing (Playwright).

---

## 6. Mobile-First & Touch Usability Standards
- **Minimum Tap Targets**:
  - All interactive touch targets (buttons, dock tabs, filter pills, close icons, links) MUST have at least `44px` height and touch area (`min-h-[44px]`, `min-w-[44px]`, or adequate tap-padding).
- **Legible Typography Scale**:
  - Readable text, card content, and form inputs MUST be at least `12px` (`text-xs` / `0.75rem`).
  - Reserve monospaced subtext strictly for FIPS IDs, telemetry, and numerical coordinates. Avoid micro-fonts (8–10px) that cause eye strain in sunlight.
- **Viewport & Scrolling**:
  - **Zero Horizontal Overflow**: Interfaces must never produce horizontal scrollbars (`document.documentElement.scrollWidth <= window.innerWidth`).
  - **Dynamic Viewport Height**: Always use `100dvh` (`h-[100dvh]`) rather than fixed `100vh` to avoid browser chrome clipping on iOS Safari and mobile Chrome.
  - **Accessible Zoom**: Never disable viewport scaling (`user-scalable=no` or `maximum-scale=1.0` are strictly forbidden).
  - **Single Active Panel**: Never stack multiple full-screen overlay panels simultaneously on mobile; enforce clean dismissals and distinct dock/tab views.
- **Responsive Testing Matrix**:
  - Test and assert across at least three mobile viewports:
    - Small compact mobile: `360×640`
    - Standard mobile (iPhone 12/13/14): `390×844`
    - Large mobile (Max/Plus): `430×932`
