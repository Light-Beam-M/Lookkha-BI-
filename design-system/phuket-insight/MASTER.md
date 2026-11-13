# Lookkha (ลูกค้า) — Design System (MASTER)

Site name: **Lookkha ลูกค้า** — "Know your Phuket customers". Tourism BI for Phuket merchants.
Style (revised 2026-11-13 by user): light, natural **sky / green / white**; deliberately *not* the dark neon "AI" look.
Background: photo of Laem Promthep (`assets/promthep.jpg`) under a white-to-mint wash. Fonts unchanged.

## Tokens
```css
:root {
  --ink: #0F2A3D;  --muted: #4B6475;  --line: rgba(15,42,61,.10);
  --card: rgba(255,255,255,.86);       /* white glass over the photo */
  --sky: #0284C7;  --sky-2: #0EA5E9;  --sky-soft: #E0F2FE;
  --green: #059669; --green-2: #10B981; --green-soft: #D1FAE5;
  --up: #15803D;   --down: #DC2626;   --radius: 16px;
}
```
- Mock tag: amber (`#FEF3C7` / `#92400E`) so "mock data" stays visible; live tag: green.

## Typography
- **Noto Sans Thai** for everything (user confirmed it reads well; do not change).

## Effects
- No neon glow, no grid overlay, no text-shadow. Soft card shadow only.
- Cards fade/rise in (50ms stagger, 400ms); off under `prefers-reduced-motion`.

## Map
- Leaflet satellite basemap (Esri World Imagery, attribution required) + leaflet.heat glow (sky → green → white).
- Zone circle markers (green, white ring), hover tooltip with zone stats, click = cross-filter. Scroll-wheel zoom off (page uses scroll-snap); zoom buttons bottom-right.

## Charts
- Nationality bars: sky gradient. Spend bars: green. Trend: actual = sky line + area, forecast = green dashed.
- Season heat map: one-hue sky ramp `#F0F9FF → #075985`. Rain: sky bars, ≥5 mm darker, green threshold line.
- Tooltip on every mark, legend when ≥2 series, "ข้อมูลจำลอง / Mock" tag on every mock chart.

## Layout
- Desktop only (min width 1280px), tested at 1440×900.
- Full-screen pages with CSS scroll-snap + right-side dot nav; sticky filter bar (period, nationality, zone, TH/EN).
  1. Overview: 5 KPIs, satellite heat map, "next week" card with filter-aware recommendations
  2. Who: nationality bar, month × nationality heat map, spend per day by nationality
  3. When: 24-month trend + 3-month forecast, 14-day rain (Open-Meteo), 60-day holidays (Nager.Date)
  4. About the data: sources, method, limitations, photo credit

## Pre-delivery checklist
- [ ] Text contrast ≥ 4.5:1 on cards over the photo
- [ ] Visible focus ring, keyboard reachable filters
- [ ] SVG icons, no emoji icons
- [ ] 1280 / 1440 / 1920px, no horizontal scroll
- [ ] `prefers-reduced-motion` respected
- [ ] Photo + map imagery credited on page 4
