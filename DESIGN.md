---
name: GeoPulse
description: A hydrographic chart of geopolitical water — buff paper, engraved ink, and tint doing the semantic work.
colors:
  paper: "#E9E7DC"
  paper-deep: "#DFDCCD"
  ink: "#16252E"
  ink-2: "#47585F"
  ink-3: "#54626A"
  survey: "#6E8CA0"
  rule: "#B6AC93"
  rule-fine: "#CCC3AC"
  globe-sphere: "#9DB9C3"
  globe-emissive: "#6F8C97"
  tint-none: "#E9E7DC"
  tint-stable: "#CCC3A4"
  tint-elevated: "#DFB24C"
  tint-breaking: "#CE7724"
  tint-conflict: "#C2185B"
  hatch-conflict: "#8E0F40"
  reverse-text: "#FFF7FA"
typography:
  display:
    fontFamily: "Spectral, Georgia, serif"
    fontSize: "25px"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "0.1em"
  headline:
    fontFamily: "Spectral, Georgia, serif"
    fontSize: "22px"
    fontWeight: 500
    lineHeight: 1.1
    letterSpacing: "0.015em"
  figure:
    fontFamily: "Spectral, Georgia, serif"
    fontSize: "21px"
    fontWeight: 600
    lineHeight: 1.1
    letterSpacing: "normal"
  italic-note:
    fontFamily: "Spectral, Georgia, serif"
    fontSize: "14.5px"
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: "normal"
    fontStyle: "italic"
  body:
    fontFamily: "Archivo Narrow, Arial Narrow, system-ui, sans-serif"
    fontSize: "13.5px"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "normal"
  caption:
    fontFamily: "Archivo Narrow, Arial Narrow, system-ui, sans-serif"
    fontSize: "11.5px"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "0.08em"
  label:
    fontFamily: "Archivo Narrow, Arial Narrow, system-ui, sans-serif"
    fontSize: "11px"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "0.19em"
rounded:
  none: "0"
spacing:
  frame: "15px"
  frame-narrow: "9px"
  panel-x: "13px"
  panel-y: "10px"
  inset-x: "16px"
  row-y: "9px"
components:
  panel-chart:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "10px 13px 12px"
  inset-panel:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "12px 16px 28px"
    width: "min(432px, 94vw)"
  button-watch:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    rounded: "{rounded.none}"
    padding: "6px 11px"
  button-watch-active:
    backgroundColor: "{colors.tint-conflict}"
    textColor: "{colors.reverse-text}"
    typography: "{typography.label}"
    rounded: "{rounded.none}"
    padding: "6px 11px"
  chip-entity:
    backgroundColor: "transparent"
    textColor: "{colors.ink-2}"
    rounded: "{rounded.none}"
    padding: "0 6px"
  input-index:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.none}"
    padding: "2px 0"
    width: "100%"
  row-register:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "6px 0"
  row-record:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.none}"
    padding: "9px 0"
---

# Design System: GeoPulse

## Overview

**Creative North Star: "The Admiralty Chart"**

GeoPulse is drawn, not rendered. The whole surface is a single sheet of buff chart paper under desk light, engraved in chart blue-black, framed by a graduated tick border and ruled into panels that each carry a title block. It refuses the arrangement its category always ships — the near-black ops console with a glowing globe, stat tiles and neon feed cards — and takes the hydrographic chart instead, because the chart tradition already solved this product's hardest problem: the Admiralty source-reliability diagram tells a navigator how far to trust each patch of survey, which is exactly a multi-source confidence model. Risk is charted danger, not a badge.

Tint does the semantic work. Bare paper means nothing was filed; graduated buff and ochre tints deepen as activity does; chart magenta under a 45° diagonal hatch marks the worst class, which is literally what magenta means on a real chart. Density is high and quiet: hairline rules at chart weights carry the structure so that no surface needs a shadow, a glow, or a card to separate from its neighbour. Every enclosure is a ruled panel sharing an edge with the sheet.

Motion is ink being laid. Panels wipe in left-to-right by clip-path at chart speed; the inset rises 6px into place; the 60-second refresh re-inks the tint layer while sounding numerals tick in fixed-width place (`font-variant-numeric: tabular-nums` is set on `body`, globally). Nothing bounces, nothing pulses, nothing breathes.

**Key Characteristics:**
- Buff paper ground with a fine fractal-noise tooth at 5% opacity — the only texture in the system
- Zero radius everywhere; zero shadows anywhere; separation is a 1px ink rule
- Two-family type: Spectral roman for chart lettering, Archivo Narrow for place names and tabular soundings
- Spectral *italic* reserved for the hydrographic convention: submerged, derived, generated
- Five-class tint ramp with no green in it, by decision
- Authored SVG marks only — no icon font, no glyph, no emoji

## Colors

A chart-paper palette: one buff ground, one blue-black ink in three weights, two rule greys, and a five-step tint ramp that carries all the meaning.

### Primary
- **Chart Blue-Black** (`{colors.ink}`): The engraving ink. Every structural rule, every panel border, every polygon outline on the globe, all headline and body text. It is the only line colour in the system.
- **Chart Buff** (`{colors.paper}`): The sheet. Page ground, panel fill (at 94% opacity where a panel floats over the globe), inset ground, and — deliberately — the "no signal" tint.

### Secondary
- **Chart Magenta** (`{colors.tint-conflict}`): The danger-area colour, and the system's only alarm. It carries the highest activity class, the pressed state of Watch, the focus ring, text selection, link hover, and input focus. Nothing else may take it.
- **Caution Hatch** (`{colors.hatch-conflict}`): The darker magenta of the 45° diagonal hatch ruled over the conflict tint — the chart's danger-area convention. Used only inside a conflict swatch.

### Tertiary
- **Survey Blue** (`{colors.survey}`): The filled portion of the reliability plot bar. It reads as measured water, not as an accent; it appears exactly once on the sheet.
- **Charted Ocean** (`{colors.globe-sphere}` sphere, `{colors.globe-emissive}` emissive at 0.5 intensity, shininess 0): The sphere material. Flat-shaded pale chart ocean — no satellite photograph, no atmosphere, graticule visible.

### Neutral
- **Ink Mid** (`{colors.ink-2}`): Label, caption, and meta-row text; the subtitle; unit glosses. The second voice.
- **Ink Faint** (`{colors.ink-3}`): Pending and deferred text, axis numerals, ISO codes, gloss text in the key, the unfilled stroke of the confidence mark.
- **Rule Grey** (`{colors.rule}`): Hairline for secondary strokes — the search underline, chip borders, close-button border, scrollbar thumb, link underline.
- **Rule Fine** (`{colors.rule-fine}`): The lightest divider, for repeating record rows and internal grid cells inside an already-bordered block.
- **Paper Deep** (`{colors.paper-deep}`): Recessed ground — the unfilled plot bar, row hover, scrollbar track.
- **Reverse Paper** (`{colors.reverse-text}`): Text on magenta only (Watch pressed, selection).

### Named Rules

**The No Green Rule.** Green never enters the tint ramp. On a hydrographic chart green means foul ground, so it cannot be made to mean "safe". Stable is a land buff (`{colors.tint-stable}`), and no-signal is bare paper: `{colors.tint-none}` is set to the exact `{colors.paper}` value on purpose, so unsurveyed areas read as blank sheet rather than as a filled state. Do not "fix" this equality.

**The Monotonic Tint Rule.** The ramp climbs in visual weight only — paper, land buff, ochre, burnt orange, magenta. A new class may be inserted only where its weight falls in order. Hue is not a dimension of the ramp; darkness is.

**The One Alarm Rule.** Chart magenta is the highest activity class and the system's focus/selection colour, and nothing else. A second alarm colour would flatten the one that matters.

## Typography

**Display Font:** Spectral (with Georgia, serif)
**Body Font:** Archivo Narrow (with Arial Narrow, system-ui, sans-serif)

**Character:** Spectral is the chart lettering — a serif with enough contrast to be engraved and enough calm to be read at figure sizes. Archivo Narrow is the place-name and sounding face: condensed, tabular, packable into a ruled register without hyphenation. The pairing is a cartographer's, not a publisher's: the serif names things, the condensed face counts them.

### Hierarchy
- **Display** (600, 25px/1, 0.1em tracking, uppercase): The wordmark in the title block. One per sheet. Drops to 21px below 820px.
- **Headline** (500, 22px/1.1): The inset title — the charted area's name, with its ISO3 trailing in Ink Faint at 15px.
- **Figure** (600, 21px/1.1): The four counts in the inset's figure grid. Serif numerals so a count reads as a sounding, not as a dashboard stat.
- **Italic Note** (400, 14.5px/1.6, italic, left ink rule at 13px indent): Generated prose only.
- **Body** (400, 13.5px/1.5, tabular numerals): Records, headlines, event rows, the index field.
- **Caption** (400, 11.5px, 0.08em, uppercase): Meta rows, source/time lines, unit glosses.
- **Label** (600, 11px, 0.19em, uppercase): Panel title blocks — "Reliability of survey", "Most active areas", "Tint key · activity class", and section rules inside the inset.

### Named Rules

**The Italic Is A Convention Rule.** Spectral italic is not emphasis. It marks the hydrographic category of things that are submerged, derived, or generated: the AI survey note, the extracted action verb in a reported relation, and the search field's placeholder. Never italicize for stress.

**The Literal String Rule.** A model identifier is a literal string and is never recased or tracked out. The generated-note title block reads "Survey note · generated by `<model>`", and the model name is exempted from the label's uppercase and 0.19em tracking (`.sec .lit`). Any machine identifier that lands in a label follows it.

**The Tabular Sounding Rule.** All numerals are tabular (`font-variant-numeric: tabular-nums` on `body`) and every count column is fixed-width (2.4em, right-aligned in the key and the active-areas register), so the 60-second refresh ticks digits in place without reflowing the sheet.

## Layout

The page is a fixed, non-scrolling sheet (`overflow: hidden` on `body`). `#sheet` is the margin: a 15px band carrying the graduated tick border, drawn as four repeating linear gradients (9px ink, 9px gap, 5px deep) on all four edges, over a 180px fractal-noise SVG tile at 0.05 opacity, over the buff ground. `#field` sits inside that margin with a single 1px ink border and clips everything.

Inside the field, the globe fills the whole clear area and panels are hung in the corners as chart blocks, each sharing its border with the sheet edge: the title block upper-left (336px), the tint key lower-left (336px), and a full-height right column (248px) holding the reliability diagram over the active-areas register. Panel borders are asymmetric on purpose — a corner block only draws the two edges that face the interior (`border-width: 0 1px 1px 0` upper-left; `1px 1px 0 0` lower-left), so no line is ever doubled against the field border. Floating panels sit at 94% paper opacity so the sphere is faintly legible behind them.

Rhythm is tight and small-numbered: 4–5px between key rows, 7–9px between a rule and the block it separates, 9–13px panel padding, 22px above a section rule inside the inset. Panel padding is `10px 13px 12px`; inset padding is `12px 16px 28px`.

**Responsive.** One breakpoint, 820px. Below it the sheet becomes a single scrolling column: the frame narrows to 9px, `#field` becomes a flex column with `overflow-y: auto`, and the four regions reorder — title block, globe (54vh, relative), tint key, right column — losing their positioning, their width, their panel background and their entrance animation, keeping only a bottom ink rule. Nothing is dropped: the key collapses to one column per row and hides only its gloss text, the active register loses its own scroll and grows with the page, the inset goes full-screen fixed, and the leader line is suppressed (it has no rectangle to point at once the globe is a band in a column). Globe altitude also changes with the breakpoint: 1.85 desktop / 2.35 narrow at rest, 1.7 / 2.2 when an inset is open.

### Named Rules

**The One Sheet Rule.** The desktop surface never scrolls. Content that outgrows its block scrolls inside that block (the active-areas register, the inset), so the sheet stays a sheet and the border stays where it was drawn.

**The Shared Edge Rule.** Panels sit flush into the corners of the field and draw only their interior-facing edges. There is no gutter between a panel and the sheet frame, and no rule is ever drawn twice.

## Elevation & Depth

**There are no shadows in this system, at all.** No `box-shadow`, no `filter: drop-shadow`, no glow, no blur, no backdrop-filter. A chart is engraved, not lit. Depth comes from three things only: the 1px ink rule (structure), the two rule greys against paper (hierarchy within a block), and the 94% paper opacity of the floating panels (the faint sense that the sheet continues underneath). Even the globe is de-lit — the sphere material runs `shininess: 0` with an emissive lift, so the sphere reads as a printed hemisphere rather than a lit ball, and `showAtmosphere(false)` removes the category's usual halo. The single altitude in the system is the 0.006 polygon lift that lets a country outline catch its own hairline; the polygon side is `rgba(22,37,46,0.18)`, an ink tick, not a drop shadow.

### Named Rules

**The Engraved Rule.** Depth is drawn, never cast. If a surface needs to separate from what is behind it, give it a 1px ink rule or a change of paper tone. Any request for a shadow, glow, blur or elevation ramp is answered with a rule.

## Shapes

Radius is zero everywhere — panels, inset, buttons, chips, swatches, the close box, the plot bar, the leader's source rectangle. Nothing in this world is rounded, because nothing on a chart is.

The form language is the ruled rectangle at three weights: **ink** (1px `{colors.ink}`) encloses a block or a figure grid; **rule** (1px `{colors.rule}`) draws secondary strokes that are interactive or subordinate — the index underline, chip and close-button borders; **rule-fine** (1px `{colors.rule-fine}`) divides repeating rows and interior grid cells inside something already bordered. Horizontal separators are these same weights as 1px filled divs (`.rule` at 9px margin, `.rule-f` at 8px).

Recurring silhouettes: the **swatch** — a 26×11 rectangle with a 1px ink border, enlarged to 34×14 on the inset's class line; the **hatch** — 45° repeating stripes, 2px on / 3px off, over the conflict tint, and only over the conflict tint; the **graduated scale** — a bordered bar with interior 1px tick marks at 25/50/75% and a numbered axis beneath; and the **source rectangle** — an 18×18 ink square drawn on the globe at the open country's centroid, joined to the inset by a two-segment leader (diagonal to a point 18px left of the inset edge, then horizontal into it at y=58).

Icons are authored SVG marks, never glyphs: the confidence mark is three stepped rectangles (3×3, 3×5, 3×7) filled to the level, and the close mark is a 1.4px-stroke X path.

### Named Rules

**The Zero Radius Rule.** No corner in this system is ever rounded. There is no radius scale to extend.

**The Hatch Means Danger Rule.** Diagonal hatching is reserved for the conflict class. It is the chart's danger-area convention, not decoration, and it may not be reused as texture, as a loading state, or as a disabled pattern.

## Components

Everything is transparent-by-default and defined by its strokes. No component in this system has a fill at rest except the conflict swatch and a pressed Watch button.

### Buttons
- **Shape:** Square (0 radius) on every variant.
- **Watch (primary action):** Transparent on paper, 1px ink border, Label type (600/11px/0.19em/uppercase), padding 6px 11px. Pressed (`aria-pressed="true"`) it fills with chart magenta and reverses to Reverse Paper. Hover shifts the border to magenta.
- **Close:** A 24×24 square with a rule-grey border holding the authored X mark; hover moves border and mark to magenta.
- **Register row (`.act-row`) and adjoining-area chip:** buttons that do not look like buttons — see below.

### Chips
- **Style:** 1px rule-grey border, transparent ground, Ink Mid text at 11px/0.04em, padding `0 6px`, zero radius.
- **State:** Entity chips are static labels; adjoining-area chips are buttons carrying `ISO3 · link-count` with the shared actors in the title. Hover darkens border and text to full ink. There is no selected state.

### Cards / Containers
There are no cards. The container is the **chart panel**: paper ground (94% opacity when it floats over the globe), 1px ink border on interior-facing edges only, `10px 13px 12px` padding, a Label title block at the top, and a `.rule` or `.rule-f` separating the title block from the contents. Shadow strategy: none, per The Engraved Rule.

### Inputs / Fields
- **Style:** The index line. Full width, no box — transparent ground, no border except a 1px rule-grey bottom edge, Body type, `2px 0` padding, preceded by an "Index" Label.
- **Placeholder:** Spectral italic in Ink Faint, per The Italic Is A Convention Rule.
- **Focus:** The bottom edge turns chart magenta. Globally, `:focus-visible` is a 2px magenta outline at 2px offset.

### Navigation
There is no nav bar. Navigation is the sheet itself: click a country on the globe, or a row in the active-areas register, and the inset draws; the URL hash carries the ISO3 so an area is linkable and deep-linkable on load. Closing restores the right column and the resting point of view.

### Registers (repeating rows)
Two row types, both bottom-ruled in rule-fine and both without any container of their own. **Register row** (active areas): swatch, name (ellipsized), right-aligned count in 600/13px, hovering to a paper-deep ground. **Record row** (events, headlines, relations): a `.who` line at 13px carrying the claim, over a `.m` line at 11.5px/0.05em uppercase Ink Mid carrying date, place, article count and the source link. The source link is never a button; it is an underlined link in the meta line.

### Reliability diagram
The chart's statement about itself, upper-right. A 17px bar with a 1px ink border on paper-deep, filled in Survey Blue to the multi-source percentage, with three 1px ink ticks at 45% opacity marking 25/50/75 and a 0–100% axis beneath. Under it, three meta rows: confirmed by 2+ sources, events filed, areas reporting. It is a measuring instrument and must never be styled as a progress bar.

### Country inset (signature)
A full-height ruled panel on the right (`min(432px, 94vw)`, full-screen below 820px) with its own sticky title block: area name in Headline, ISO3 trailing, "Inset A" as a Label designation, close square at the top-right. Body order is fixed: class line (swatch + class name + window), Watch, Counts figure grid (2×2, ink-bordered, rule-fine interior cells), generated survey note, adjoining areas, reported actions, headlines, events. It is tied to the globe by a **leader line** drawn every frame: an 18×18 source rectangle at the country's centroid, a diagonal, and a short horizontal into the panel edge — the way a chart ties an inset to its source rectangle. The leader clears itself when the centroid rotates past the visible hemisphere (`cos > 0.25`), when it would collide with the panel edge, and below 820px.

**The inset carries no scale bar, by decision.** A country inset hung off a 3D globe states no linear relation, and the only candidate — a time axis across the 3-day window — would have to be drawn from the 25 events the endpoint returns, fabricating a distribution from a truncated set and breaking product principle 4 (fabricate nothing). If a ruler is ever genuinely wanted there, the only honest one is this country's violent share measured against the surveyed maximum, drawn from the complete `/api/countries` rows — optional, and not owed.

## Do's and Don'ts

### Do:
- **Do** let tint carry meaning and keep everything else ink on paper. Five classes, monotonic in weight, magenta only at the top.
- **Do** set "no signal" as bare paper. `{colors.tint-none}` equals `{colors.paper}` deliberately; an unsurveyed area is a blank sheet, not a filled state.
- **Do** enclose in ruled panels with a Label title block, flush to the sheet corners, drawing only interior-facing edges.
- **Do** reserve Spectral italic for the generated, derived, and submerged, and keep every numeral tabular so the 60-second re-ink ticks in place.
- **Do** author icons as inline SVG marks sized 11–14px, stroked in ink.
- **Do** keep the desktop sheet unscrolling: overflow scrolls inside its own block.
- **Do** describe the survey's own reliability on the sheet. The chart states how far to trust itself; that block is not optional furniture.

### Don't:
- **Don't** introduce green anywhere in the activity ramp. Green is foul ground on a chart and cannot be made to mean safe.
- **Don't** add a shadow, glow, blur, backdrop-filter, or elevation ramp. Depth is drawn with a 1px rule.
- **Don't** round a corner. There is no radius scale.
- **Don't** use hatching for anything but the conflict class, or magenta for anything but the top class, focus, and selection.
- **Don't** ship a card, a stat tile, a neon feed row, a glowing globe or an atmosphere halo — the near-black ops console is the confirmed anti-reference.
- **Don't** use an icon font, emoji, or a third-party glyph set.
- **Don't** recase or track out a machine identifier that lands inside a label.
- **Don't** draw a ruler, axis, or scale that the data cannot honestly support, and never draw a distribution from a truncated response.
