# jjiroo-tancheon-duck-chase-002 Style Lock

## Basis

- episode slug: `jjiroo-tancheon-duck-chase-002`
- production mode: `reference-only`
- canonical character folders: `characters/jjiroo` missing, `characters/jjonga` missing
- source packet: `../source-packet.json`
- original-style basis: `../../jjiroo-tancheon-duck-chase-001/storyboard/style-lock.md`
- target output: vertical `9:16` storyboard/webtoon cuts for downstream `BRIEF`

## Style Foundation

- Preserve the same original drawing style basis from `001`. Do not beautify, repaint, or reinterpret into a different illustration style.
- Warm observational pet webtoon look, clean linework, soft painterly shading, bright daytime riverside air.
- Keep Tancheon geography readable across all cuts: dirt walking path, grass edge, shallow river, duck rest area, and a clear climb-out bank must feel like one continuous location.
- Expressions may be comedic and readable, but never cruel, horror-coded, or rescue-disaster melodrama.
- Do not place any text, subtitle, number, logo, watermark, or UI artifact inside generated imagery.

## Cast Lock

- `찌루 / Jjiroo`: small cream-ivory dog, upright triangle ears, short clear muzzle, round dark eyes, slightly curled fluffy tail, mint Y-harness. He is curious, fast, impulsive, and confident in water without reading as aggressive.
- `쫑아 / Jjonga`: slightly smaller caramel-brown dog, floppy ears, rounder face, short legs, peach harness. Calmer observer energy. Must be immediately distinguishable from Jjiroo.
- `어머니`: supporting guardian only. Present in setup and rescue escalation, but never framed as the protagonist.
- `탄천 오리들`: alert wild ducks that escape safely. They are a flight trigger, not prey and not victims.

## Continuity Rules

- Jjiroo's mint Y-harness and Jjonga's peach harness are locked in every cut.
- Dog breed feel, fur color, ear shape, eye shape, body size, and tail silhouette must not drift between cuts.
- The action order is locked: calm walk -> curious sniffing -> duck spotting -> stealth/stalk -> breakaway chase -> river entry -> mother jumps in -> mother falls behind -> Jjiroo exits on his own -> ironic final look.
- The climax must always show Jjiroo entering the river first and the mother entering later.
- The ending must always land with Jjiroo already back on shore while the mother remains wet in the water or just behind him.

## Tone And Safety

- Core tone: true funny pet anecdote, escalating mishap, clean ironic payoff.
- Allowed intensity: surprise, urgency, comic speed, mild rescue concern.
- Forbidden tone: drowning panic, predatory violence, duck capture success, injury, cruelty, horror rescue, hyper-realistic danger.
- Wildlife and pets must read safe by the end of every action beat.

## Shared Negative Prompt

- duplicate pet
- second version of same dog
- extra dog
- extra animal
- wrong pet identity
- wrong fur color
- wrong harness color
- wrong ear shape
- merged face
- broken anatomy
- extra limbs
- wings
- duplicated head
- unreadable river geography
- realistic photo style drift
- glossy anime repaint
- horror tone
- drowning panic
- duck injury
- bite attack
- gore
- text
- letters
- subtitles
- numbers
- logos
- watermarks

## Reusable Prompt Block

- environment: bright daytime Tancheon riverside path, dirt trail, grass edge, shallow flowing river, readable bank and climb-out point
- art direction: expressive vertical webtoon illustration, clean lines, soft shading, original `001` style preserved
- protagonist lock: same cream-ivory dog Jjiroo, upright triangle ears, round dark eyes, curled fluffy tail, mint Y-harness
- supporting dog lock: same caramel-brown dog Jjonga, floppy ears, rounder face, short legs, peach harness
- human lock: mother remains readable but secondary to Jjiroo
- behavior lock: comic anecdote only, no cruelty, no injury, no prey violence

## Generation Notes

- Use this file as the shared style preamble for every storyboard cut prompt.
- Each cut prompt must also declare cast cardinality before describing action.
- If action-heavy cuts cause identity drift, shorten the action span rather than changing the style or pet design.
- Until canonical character folders exist, treat this episode-local lock as the controlling visual canon for `002`.
