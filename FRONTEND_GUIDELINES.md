# FRONTEND_GUIDELINES — EpiSense

---

## Design Philosophy

Medical/public-health dashboard. Trust and clarity above everything. No decorative chrome. Data is the UI.

---

## Color System

### Semantic Palette (Tailwind config `tailwind.config.ts`)

```typescript
colors: {
  // Brand
  brand: {
    DEFAULT: '#1D6FA4',   // Primary blue — buttons, links, active states
    light:   '#E8F4FB',   // Light blue — selected state backgrounds
    dark:    '#145580',   // Dark blue — hover states
  },

  // Risk Tiers (choropleth + badges)
  risk: {
    low:      '#22C55E',  // Green  — score 0–39
    medium:   '#F59E0B',  // Amber  — score 40–59
    high:     '#EF4444',  // Red    — score 60–79
    critical: '#7F1D1D',  // Dark red — score 80–100
  },

  // Neutral (UI chrome)
  surface:   '#F8FAFC',   // Page background
  card:      '#FFFFFF',   // Card background
  border:    '#E2E8F0',   // Default border
  muted:     '#94A3B8',   // Muted text, placeholders
  text: {
    primary:   '#0F172A', // Headings
    secondary: '#475569', // Body
    inverse:   '#F8FAFC', // Text on dark backgrounds
  },
}
```

### Usage Rules

- Never use raw Tailwind colour classes (`blue-500`) directly in component JSX. Always use the semantic tokens above (`text-brand`, `bg-risk-high`).
- Alert banner background: `bg-risk-high/10` (10% opacity), border `border-risk-high`.
- Chart colours:
  - Predicted risk line: `#1D6FA4` (brand).
  - Confirmed cases bars: `#94A3B8` (muted).
  - Forecast region fill: `#E8F4FB` (brand-light).

---

## Typography

```css
/* Base */
font-family: 'Inter', system-ui, -apple-system, sans-serif;

/* Scale (px → Tailwind class) */
h1   → text-2xl font-semibold   (24px) — page titles
h2   → text-xl  font-semibold   (20px) — section headers
h3   → text-lg  font-medium     (18px) — card titles
body → text-sm  font-normal     (14px) — default body
small→ text-xs  font-normal     (12px) — captions, meta, chart labels
```

Load Inter via Google Fonts CDN in `index.html`:
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
```

---

## Spacing System

Tailwind's default 4px base unit. Stick to these increments: 4, 8, 12, 16, 20, 24, 32, 40, 48.

- Card inner padding: `p-6` (24px).
- Section gap: `gap-6` (24px).
- Sidebar width: `w-72` (288px), fixed.
- Main content max-width: `max-w-screen-xl mx-auto`.

---

## Component Specifications

### RiskBadge

```tsx
// Usage: <RiskBadge score={78} />
type Tier = 'low' | 'medium' | 'high' | 'critical';

function getTier(score: number): Tier {
  if (score < 40) return 'low';
  if (score < 60) return 'medium';
  if (score < 80) return 'high';
  return 'critical';
}

const tierStyles: Record<Tier, string> = {
  low:      'bg-green-100 text-green-800 border-green-200',
  medium:   'bg-amber-100 text-amber-800 border-amber-200',
  high:     'bg-red-100   text-red-800   border-red-200',
  critical: 'bg-red-900   text-red-100   border-red-800',
};

// Renders: rounded pill, 24px height, 8px h-padding, border-1
```

### AlertBanner

```tsx
// Shown at top of /district/:id when score > 70
// Background: risk-high/10, left-border 4px solid risk-high
// Contains: icon (AlertTriangle), message, Acknowledge button (outline)
```

### Choropleth Map

- Library: `react-simple-maps` + `d3-scale` for colour interpolation.
- GeoJSON: India district-level TopoJSON (compressed, bundled in `/public/data/india-districts.topojson`).
- Projection: `geoMercator`, centered `[82.8, 22.5]`, scale `950`.
- Fill: `scaleQuantize` domain `[0, 100]` → 5 colour stops (green to dark red).
- Hover: tooltip showing district name + risk score. CSS `cursor: pointer`.
- Click: `navigate('/district/' + districtId)`.
- No zoom controls needed for hackathon demo.

### Time-Series Chart

- Library: `Recharts` `ComposedChart`.
- Left Y-axis: risk score 0–100.
- Right Y-axis: confirmed cases (auto domain).
- X-axis: date string `MMM dd`.
- Forecast region: `ReferenceArea` with `fill="#E8F4FB"` and `label="Forecast"`.
- Tooltip: custom styled with `bg-white border border-border shadow-md p-3 rounded-lg text-sm`.
- Responsive: `ResponsiveContainer width="100%" height={320}`.

### SHAP Bar Chart

- Library: `Recharts` `BarChart` horizontal layout.
- Bars: positive SHAP value (increases risk) → `fill="#EF4444"`, negative → `fill="#22C55E"`.
- Feature names on Y-axis: truncated to 24 chars.
- No legend (colour semantics are self-evident with +/- direction).

### Sidebar Layout

```
<aside className="w-72 flex-shrink-0 border-r border-border bg-card h-screen sticky top-0 overflow-y-auto p-4">
```

### DataCard (metric summary card)

```tsx
// 3-column grid for environmental factors
// Structure: icon (top-left), metric name (muted), value (large, primary), trend sparkline
// Border: 1px solid border, rounded-xl, bg-card, p-5
```

---

## Responsive Breakpoints

| Breakpoint | Width | Behaviour |
|------------|-------|-----------|
| sm | 640px | Single column layout |
| md | 768px | Sidebar collapses to top filter bar |
| lg | 1024px | Full sidebar + map layout |
| xl | 1280px | Max-width container |

Sidebar collapses on `< md`. Map becomes full-width. Tab nav replaces sidebar filters.

---

## Loading States

- Map loading: skeleton rectangle `animate-pulse bg-slate-200 rounded` same dimensions as map.
- Chart loading: skeleton lines at chart height.
- Table loading: 5 skeleton rows.
- Buttons: `disabled` + spinner icon (Lucide `Loader2` with `animate-spin`).

---

## Error States

- API error: `<ErrorState icon={AlertTriangle} title="Failed to load data" message={error.message} retry={refetch} />`.
- Empty filter result: `<EmptyState icon={SearchX} title="No districts match" message="Try adjusting your filters." />`.

---

## Form Patterns

- All forms use React Hook Form + Zod.
- Error messages: `text-xs text-red-600 mt-1` below input.
- Input base class: `w-full rounded-lg border border-border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand`.
- Disabled state: `opacity-50 cursor-not-allowed`.
- Submit button: `bg-brand text-white hover:bg-brand-dark disabled:opacity-50`.

---

## Animation

- Page transitions: none (keep it fast, medical context).
- Tooltip appear: `transition-opacity duration-150`.
- Alert banner slide-in: `transition-transform duration-200 translate-y-0` from `-translate-y-2`.
- Chart re-render: Recharts default animation `isAnimationActive={true}` (keep as-is).
- Skeleton pulse: Tailwind `animate-pulse`.

---

## File Structure (Frontend)

```
src/
  api/           → axios instance + API call functions (auth.ts, districts.ts, alerts.ts, predict.ts)
  components/    → Shared components (RiskBadge, AlertBanner, DataCard, Navbar, Sidebar)
  pages/         → One file per route (Dashboard, District, Alerts, Simulator, Reports, Admin, Login)
  store/         → Zustand stores (authStore.ts, alertStore.ts)
  hooks/         → Custom hooks (useDistrict, useAlerts, usePredict)
  types/         → TypeScript interfaces (District, Alert, PredictRequest, User)
  utils/         → Helper functions (formatDate, getRiskTier, formatScore)
  lib/           → shadcn/ui utilities (cn, utils)
```
