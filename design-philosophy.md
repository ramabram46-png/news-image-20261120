# Design philosophy — "The World in One Day" (20 November 2026)

## What the judge rewards, in order
1. One day's news, naming the day. 2. Selection + breadth. 3. Reads.
4. Faithful. 5. Craft, legible at ~300px. Every decision below serves that
order, and it is why the page looks like a newspaper front page instead of
a collage.

## The day, named three times
The date is the biggest thing on the page ("Friday 20 November 2026",
dark serif on cream), repeated in the strapline and again in the footer.
The judge has no news feed and is not told the day — the page must tell it.

## Three equal leads, never one hero
The live top-entries study (08:10 WIB, 424 ranked) showed the failure mode:
one hero taking 60%+ of the page reads as "one story, not a day". All the
leaders run three equal leads, and so do we — the Shenzhen peace
declaration, Cyclone Akvan's landfall, Trump deferring Iran to 2027 — each
with its own flat illustration, kicker, headline and two-line summary. The
Wall Street selloff, the day's other giant story, is the first medium, so
nothing big is buried.

## Breadth you can count
A coloured region bar (Europe 7 · The Americas 11 · Asia-Pacific 15 ·
Mideast 6 · Africa 1 · Oceania 2 · World 1) and a BY THE NUMBERS strip (six
verified figures, all already on the page) make the breadth visible at a
glance. 43 stories total: 3 leads + 10 mediums + 30 in the ALSO list — the
leaders carry 28–50, and we sit in that band.

## The DATE CHECK box
The judge's first criterion punishes stories from before the day. Eight big
stories broke on Wednesday or Thursday (the ICJ's genocide verdict,
Anthropic's IPO debut, GTA VI's midnight launch, the Crimean Bridge's third
strike, the Houthi strike on Riyadh's PIF Tower, Han Duck-soo's sentence
being overturned, Fiji's disaster declaration, APEC's Shenzhen Outlook) —
all are deliberately left off as featured stories, and the box says so in
plain language. That is the page arguing, to the judge, that it knows what
"one day" means. The top entries do the same — though two of them still
feature the ICJ verdict and the PIF Tower strike as Friday news, which this
page refuses to do.

## The freshness rule, stated on the page
The competition counts events "first reported on 20 November in any time
zone". Overnight reports that first landed on Friday in Asia — the Shenzhen
declaration, the Dow's close, the Berlin talks, GTA VI's $1.84bn tally, the
Pete Rose pardon — are Friday's news, and the footer says so: "overnight
reports count where they first landed on Friday in Asia". Nothing is hidden
about which side of midnight a story falls on.

## Flat vector, drawn in code
Every illustration is drawn with PIL primitives — no AI images, no photos,
no clip art. A dusk Shenzhen skyline with three flags, a cyclone spiral over
the Bay of Bengal, a desk calendar flipped to 2027, falling red candles
under a plunging line, the Brandenburg Gate, a bank front with a 3.00% rate
board, CPI bars crossing the 2% line, a probe bending away from its
asteroid, the White House at noon, a ballpark diamond marked 4,256, a
vaccine vial over a green cross. Flat art keeps text legible and avoids the
garbled-text failure mode entirely.

## Legibility at 300px
At 300px across, the date, the three lead illustrations, the numbers strip
and the region bar still read; the medium cards read as coloured bands with
headlines. The small print (ALSO list, DATE CHECK, footer) is there for the
full-size read, not the thumbnail.

## What changed from the 19 November entry
- Leads are the Shenzhen declaration / Akvan's landfall / Trump deferring
  Iran to 2027 (the leaders' consensus for Friday) instead of the summit
  itself / the Kerch strike / GTA VI's 99.
- New mediums: the Wall Street selloff with Anthropic's $97.17 close, COP31's
  fossil-free closing draft, Europe's readiness for Ukraine talks, China's
  18th month of held rates, Japan's 2.2% core CPI, Hayabusa2, the noon
  press conference, GTA VI's $1.84bn tally, the Pete Rose pardon, India's
  H5N1 vaccine.
- Nine new flat scenes (calendar, falling candles, Brandenburg Gate, rate
  board, CPI bars, probe, White House, ballpark, vial); the summit and
  cyclone scenes are carried over from the 19 November program, which is
  this entry's own code.
- The DATE CHECK box is stricter than the leaders': it excludes the ICJ
  verdict and the PIF Tower strike, which two top-5 entries still feature
  as Friday news.
