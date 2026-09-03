---
name: Maritime Intelligence System
colors:
  surface: '#f7f9fc'
  surface-dim: '#d8dadd'
  surface-bright: '#f7f9fc'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f4f7'
  surface-container: '#eceef1'
  surface-container-high: '#e6e8eb'
  surface-container-highest: '#e0e3e6'
  on-surface: '#191c1e'
  on-surface-variant: '#42474d'
  inverse-surface: '#2d3133'
  inverse-on-surface: '#eff1f4'
  outline: '#73777e'
  outline-variant: '#c3c7ce'
  surface-tint: '#406182'
  primary: '#001629'
  on-primary: '#ffffff'
  primary-container: '#002b49'
  on-primary-container: '#7293b6'
  inverse-primary: '#a8caef'
  secondary: '#0058bc'
  on-secondary: '#ffffff'
  secondary-container: '#0070eb'
  on-secondary-container: '#fefcff'
  tertiary: '#1d0048'
  on-tertiary: '#ffffff'
  tertiary-container: '#36007b'
  on-tertiary-container: '#a376ff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#cfe5ff'
  primary-fixed-dim: '#a8caef'
  on-primary-fixed: '#001d34'
  on-primary-fixed-variant: '#274969'
  secondary-fixed: '#d8e2ff'
  secondary-fixed-dim: '#adc6ff'
  on-secondary-fixed: '#001a41'
  on-secondary-fixed-variant: '#004493'
  tertiary-fixed: '#eaddff'
  tertiary-fixed-dim: '#d2bbff'
  on-tertiary-fixed: '#25005a'
  on-tertiary-fixed-variant: '#5a00c6'
  background: '#f7f9fc'
  on-background: '#191c1e'
  surface-variant: '#e0e3e6'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  kpi-value:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 34px
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-caps:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.06em
  metadata:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  container-margin: 24px
  gutter: 20px
  card-padding: 24px
  section-gap: 32px
---

## Brand & Style

This design system is engineered for high-stakes maritime logistics and global supply chain intelligence. It merges the precision of industrial command centers with the sophisticated spatial aesthetics of modern high-end consumer technology. 

The visual direction follows a **Modern Corporate** style with **Glassmorphism** accents. It prioritizes clarity, technical rigor, and a "calm-tech" philosophy. The interface should feel like an advanced navigational tool—authoritative yet approachable, utilizing vast white space to reduce cognitive load while managing dense operational data. 

**Key Brand Pillars:**
- **Industrial Precision:** Every pixel serves a functional purpose; alignments are rigorous.
- **Oceanic Intelligence:** A palette and motion language inspired by the depth and fluidity of global waters.
- **Operational Clarity:** High-contrast typography and clear hierarchy ensure critical insights are surfaced instantly.

## Colors

The color system is built upon a foundation of "Cool Porcelains" and "Deep Maritime Navies."

- **Foundation:** The primary background uses a subtle cool gray (`#F5F7FA`) to prevent eye fatigue during long operational shifts.
- **Brand Navy:** Used for primary text and high-importance UI elements to convey stability and authority.
- **Electric Blue:** Reserved for primary actions, active states, and critical navigational paths. 
- **AI Violet:** A distinct purple hue is used exclusively for predictive analytics, machine learning insights, and automated recommendations.
- **Semantic Status:** High-saturation tokens for risk levels (Green/Amber/Red) are utilized with sufficient contrast against white surfaces to ensure accessibility.

## Typography

This design system utilizes **Inter** for its neutral, highly legible, and technical character. 

- **Numerical Precision:** KPI values use a semi-bold weight with tighter letter spacing to appear as unified "blocks" of data.
- **Metadata Labels:** Small uppercase labels are used for category headers and secondary data points to create visual distinction from body content without increasing font size.
- **Hierarchy:** Use font weight rather than size to differentiate importance in dense data tables.
- **Mobile Scaling:** Headline sizes should scale down by 20% on mobile devices, while body text remains consistent at 14px-16px for legibility.

## Layout & Spacing

The layout follows a **Fixed-Fluid Hybrid** model. The sidebar remains fixed at 260px, while the main content area utilizes a 12-column fluid grid.

- **Rhythm:** A 4px base unit governs all spacing.
- **Grid:** On desktop (1440px+), content is contained within a 12-column grid with 20px gutters. On tablet (768px-1023px), margins reduce to 16px and the sidebar collapses to an icon-only rail.
- **Density:** High-density data tables use 8px vertical cell padding, while "Executive Overview" cards use 24px internal padding to create a more premium, airy feel.

## Elevation & Depth

Hierarchy is established through a four-tier elevation system that mimics spatial layers.

1.  **Level 0 (Base):** The canvas. A solid, non-interactive cool gray.
2.  **Level 1 (Surface):** Primary cards and containers. Solid white with a very thin (1px) neutral-200 border. No shadows.
3.  **Level 2 (Float):** Glassmorphic overlays, dropdowns, and active navigation states. These use `backdrop-filter: blur(12px)` and a 60% translucent white background. They feature a soft, 10% opacity navy shadow.
4.  **Level 3 (Alert/AI):** Floating modals and AI-driven insights. These use a slightly thicker "frosted glass" effect with a subtle inner light refraction (a 1px white top border) to appear physically elevated.

## Shapes

The design system employs a "Tactile Rounded" language. 

- **Standard Elements:** Buttons, input fields, and small cards use a **12px (0.75rem)** radius.
- **Container Elements:** Large dashboard modules and main surface containers use a **16px (1rem)** radius to feel modern and premium.
- **Interactive States:** Hovering over list items or menu links should trigger a 8px rounded background highlight.
- **Consistency:** Avoid pill-shapes except for status badges (Tags) and specific toggle switches.

## Components

### Buttons
- **Primary:** Solid Deep Navy (`#002B49`). White text. 16px height-padding. 1px inner light border for a tactile "pressed" feel.
- **Secondary (Glass):** Frosted glass background. Deep Navy text. 1px border with 20% opacity.
- **AI Action:** Gradient border (Blue to Violet) with a glass core.

### Cards & Modules
- Cards must have a clear header area with a `label-caps` title. 
- Content within cards should be separated by subtle 1px dividers rather than shadows.

### Navigation
- Sidebar icons use a dual-tone style (Navy and Electric Blue).
- The "Active" state is represented by a glassmorphic pill background that slides vertically between items.

### Data Visualization
- Charts should use thin stroke weights (1.5pt - 2pt).
- Points of interest on maps use "pulsing" glass rings to indicate real-time activity.

### Input Fields
- Subtle gray background (`#F1F5F9`) that transitions to a white background with an Electric Blue border on focus.