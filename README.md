# 20 November 2026 — World News in One Image

[![make.fun](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/ramabram46-png/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/ramabram46-png/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120)

A newspaper front page summing up Friday 20 November 2026 in a single
1024×1024 image: 43 stories across 7 regions, with a dark-navy world map
marking where each featured story happened and a THE DAY IN UTC strip
telling the day as it unfolded.

## The image

Built under the "The World in One Day" philosophy (`design-philosophy.md`):
cream paper, a huge dark serif date, a red strapline naming the three leads,
a THE DAY IN UTC timeline strip, a coloured region bar, a BY THE NUMBERS
strip, three EQUAL leads (never one hero taking 60%+ of the page), ten
medium stories as numbered cards (04–13), a dark-navy world map with red
numbered pins, a 30-item "Also on Friday 20 November" list, and a DATE
CHECK box naming the big stories that were left off because they broke
before Friday.

- **3 lead stories:** Trump, Xi and Putin issue a joint peace declaration in
  Shenzhen (four points, no Ukraine, no Iran); Cyclone Akvan makes landfall
  near Gopalpur at noon with 300,000 evacuated; Trump puts the Iran decision
  off to 2027.
- **10 medium stories:** Wall Street slides as the AI rally breaks (Dow
  −1,101; Anthropic closes $97.17, up 17%); COP31's closing day, with fossil
  fuels cut from the draft; Europe ready for Ukraine talks with Russia;
  China holds loan rates for an 18th month; Japan's core inflation hits
  2.2%; Hayabusa2 gives up its asteroid landing; Trump's noon press
  conference; GTA VI passes The Odyssey with $1.84bn in a day; Trump
  pardons Pete Rose; India dedicates its first home-made H5N1 vaccine.
- **30 more** in the "Also on Friday 20 November" list, plus a map with
  red numbered pins for stories 1–13 and grey dots for the briefs.

Every featured story was checked against at least two independent news
sources (Reuters, AP, BBC, Al Jazeera, Sensor Tower, IMD, Nasdaq, Bank of
Japan, PBOC and others) on 20 November 2026 — see
`research-20-nov-2026.md` for the sources, the freshness rule, and why
these leads. All illustrations are flat vector art drawn in code; no
AI-generated imagery, so no garbled text and no fake photos.

## How it is built

`draw_poster.py` (Python 3, Pillow, Noto fonts) draws `entry.png`
deterministically from the story list in the script. `main.ts` (Node 22,
standard library only) copies the embedded `entry.png` byte-for-byte to
`/output/entry.png` — no network, no randomness, no timestamps, so repeated
runs produce identical bytes.

```sh
python3 draw_poster.py entry.png   # regenerate the poster
node main.ts                       # write /output/entry.png
```

## Licence

MIT — see `LICENSE`.
