# Adventure game idea (spitballing, Nov 5, 2026)

**Status: an idea only. Nothing here is approved or planned to be built.** The owner got bored of the Colosseum as it is while playtesting and wants more lasting fun. This is one possible direction, written down so it is not lost.

## The idea
A solo adventure game for one person on one device, using the Colosseum as the fight screen for encounters. The story lives in campaign files, so more campaigns can be written without changing the engine. The first adventure would be a free demo, and later campaigns could be paid add-ons. The owner will not do anything about marketing until a demo exists.

## Shape (small to start)
- A small node map: towns, rooms and forks, with a scene at each node.
- Scenes are text with choices, fights, shops or loot, rest, and endings.
- A campaign save: current scene, gold, items, flags, who is alive. It sits beside the roster in browser storage.
- Example fight the owner wants: 2 orcs and an orc shaman.

## Campaign file (sketch, one JSON file per campaign)
- Info: title, author, version, start scene, recommended character points.
- Scenes: id, title, text, choices. A choice has a target scene and optional conditions (has item, gold at least N, flag set).
- Scene types: text, fight (enemies, map, where to go on a win, loss or escape), shop or loot, rest, end.
- Effects: give gold, XP or an item, set a flag, heal.
- Custom creatures defined inside the campaign, so orcs and the shaman live in the campaign and not in the engine.
- A validator that catches broken links, dead ends and unreachable scenes.

## Pieces, in a possible order (one feature at a time)
1. Campaign format and validator.
2. Scene player with the campaign save.
3. Fight bridge: start a Colosseum fight with a chosen set of enemies and get back who survived, XP, and win, loss or escape. This is the main change to existing code.
4. Node map view.
5. A short demo of about 6 to 8 scenes.
Later, maybe: an editor for writing campaigns without hand-editing JSON.

## Dependency to know about
The orc shaman needs computer-run wizards in the Colosseum, which is on the backlog and not started (the Colosseum Gladiator never casts). Either build that first, or start the shaman as a fighter-style stand-in with a couple of scripted attacks.

## Android
Not a "compile JSON to APK" job. The game is a web app, so it would be wrapped in an app shell (Capacitor, or a PWA or Trusted Web Activity). Build and test the web version first. Things to handle: saves live in browser storage (add an export or backup), voice chat needs mic permission, Google Play Billing rules apply to digital content sold inside a Play Store app, and store account and testing requirements change, so check them when the time comes.

## Marketing and licence (things to check, not advice)
- The Fantasy Trip belongs to Steve Jackson Games, so ask them what is allowed for fan products before selling anything. Original world and encounters help but may not settle it.
- The site is static and the repo is public, so paid campaign files must stay out of the repo, and they cannot be truly locked. Options: sell a file the player loads into the game (simple, can be shared), or serve it from Firebase behind a purchase code or account (more work).
- A free demo that ends on a cliffhanger with a link to paid campaigns is the usual model. Playtesters could come from the SJG forums, Discord and Reddit.

## Open questions
- Does this give the lasting fun the owner is after? A small solo prototype would answer that before committing to more.
- Ask SJG about licensing before or after the demo exists?
- Rules: stay on the 2018 Melee rules, or add Wizard-style items?
- Write the first adventure by hand, or build an editor?
