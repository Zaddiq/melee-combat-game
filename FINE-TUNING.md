# Colosseum: fine-tuning handoff (written Nov 5, 2026)

Paste or attach this at the start of the new chat. Repo: Zaddiq/melee-combat-game, site https://zaddiq.github.io/melee-combat-game/. Main is up to date and pushed (last commit 9ff70e9). Also read HANDOFF.md, NOTES.md and PROGRESS.md in the repo.

## State
Everything requested so far is built, tested and live: phone layout (sticky map, choices, results), phone start hex and facing, Fight a friend online, multi-hex spells as dragon footprint, voice chat, drawn art as counters and avatars, original black-and-white blank sheet and filled-in builder printout, solo-playtest phone fixes, opponent armor bug fix (computer no longer wears hidden creature armor), and "The computer's side" card shown when a fight starts.

The owner is now only tweaking from playtests. They report issues as they find them. Work style: one feature per branch, run the tests, ff-merge to main, push, tell the owner to hard-refresh. database.rules.json changes must be re-pasted by the owner in the Firebase console.

## Waiting on the owner
1. Do Colosseum fights feel fair now after the armor fix? Their last playtest: 33-point fighter, ST 12, broadsword, vs a computer fighter that stopped 7 hits and needed 12 to hit. Cause was the hidden-armor bug. The owner guessed opponent DX 18, but opponent ST+DX is always equal to the player's.
2. If fair, build the easy start. Proposal: handicap of 4 at 32 points, shrinking to 0 at 36 and up, plain weapon for the computer, an "Easy opponent" line. Needs their OK.
3. Wizard strength: opponent sizing only uses ST+DX, but wizard IQ matters. Proposal: a wizard strength rating with one tunable IQ constant. Not approved yet. (Unlimited Arena makes wizards, about 1 in 4 opponents. The Colosseum Gladiator never casts.)
4. Real-friend tests of voice chat and Fight a friend online (WebRTC with STUN only, no TURN, so some networks may fail).
5. Ask the owner what their "different idea" was (forgotten earlier).

## Backlog (not started)
Megahex Avert (shared upkeep); facing choice and preview for multi-hex shapes; computer-run wizards in the Colosseum; compact phone setup and outdated intro text; computer-run seats; weapon-limit lifting (change NOTHING until told); how-to-play page; feedback button; stomp; encounter page; pictures in Arena/Duel; hide-pictures host switch; splash art (needs written artist permission); Hall of Fame from the Colosseum.

## Facts worth remembering
- Owner's pen name is Zaddiq (LICENSE holder). Prints black and white only: no color fills or CSS gradients in print.
- Test setup: Playwright with `?net=mem`; suites in tests/ (colosseum, colosseum_solo, colosseum_start, online_*, avatar, voice, multihex_spells, opponent_gear, spend_tablet). All passed at the last commit.
- Key files: colosseum.html (host and Gladiator), online-host.js, phone.html, phone-map.js, net.js, voice.js, builder.html, sheet.html, rules.js, database.rules.json. Opponent generation: `makeOpponent(total)` and `bestGear` (colosseum.html, duel.html); wizard-arena.html uses its own armor list.
