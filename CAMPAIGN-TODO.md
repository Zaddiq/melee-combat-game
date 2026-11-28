# Campaign game: where we are and what is left (written Nov 28, 2026)

Read this first in a new chat, then HANDOFF.md and NOTES.md (NOTES.md has one section per feature, newest at the bottom).

## What this is
- Repo Zaddiq/melee-combat-game, live at zaddiq.github.io/melee-combat-game/.
- The old Colosseum and builders (files outside `campaign/`) are the stable game for the kids' Arena play. Do not touch them.
- The campaign game lives in `campaign/` (a full copy that can deviate): menu `campaign/index.html`, builder `campaign-builder.html`, host tablet `colosseum.html`, phones `phone.html`, simulator `sim.html`.
- Rules basis: 2018 Melee/Wizard, plus the 1980 Advanced Melee / Advanced Wizard / In the Labyrinth for anything missing. The owner no longer owns the 2018 book; he checks against photos he sent and the 1980 PDFs.
- Keep out of the public repo: module text/data (Red Crypt etc.), book wording, advanced spell descriptions (those live in his private rules-data file). Starter data in the repo is names, levels, costs and prices only.
- Workflow: one branch per feature, tests with `python3 tests/<name>_test.py` (Playwright), merge to main only when he says "merge". The stop hook about "unpushed commits" is a false alarm (check with `git push -u origin <branch>` and `git ls-remote`).

## Built and live on main (this long chat)
Rules data file/starter data/table sharing to phones; weapons shop and armor columns; spell picker (124 spells) with descriptions; Sword includes Knife; $1000 starting purse; bastard sword grip; weapon+shield ready after a bow; Red Crypt module loader; dragon duplicates fixed; **Host a campaign table** menu button (continues the module at the saved room, opens the phone table, campaign ST on); **Premade fighters** card at the table (8 premades + bench A/B, given to a tablet or phone seat); **bench flow** (simulator "Send to bench", builder "Load bench A/B" which also buys gear and trains the talents it needs); **bigger text** (15-16px minimum) and a phone-friendly shop.

## Not merged / shelved
- `seven-players` (local branch only, not pushed): 7 players as three teams (3 + 3 + him solo). Started, setup and entrances worked, the fight start was not finished. He said never mind (they will not have that many again). Pick it up only if he asks.

## Still to do / open (his order not set; ask which first)
1. **Avert**: he said it "never worked". Tested: it works mechanically, but casting misses at range and drains ST, with no visible cue. Waiting for what he saw. Ideas: log line when it takes effect, a map marker, an ST warning.
2. **"undefined" error after a forced retreat** (human vs human duel in the Colosseum): could not reproduce (about 90 random fights, none). If it happens again he will send a screenshot of the message and the last fight-log lines.
3. **Colosseum spells**: only 59 of 124 spells work in fights. Offer a shortlist and let him choose which to add.
4. **Heroes with spells cannot cast in the Colosseum yet** (casting is wizard-only), and the builder has no "New wizard" button.
5. **Phone-layout pass**: his son (tech-minded, interested in the code) and daughter (dislikes phone formatting) are possible helpers. The Colosseum host page still scrolls sideways at phone width (left because it is the tablet view); check the phone results screen if text is still too small.
6. Smaller offers he has not answered: a file chooser for loading a module, a "how to help" page in the repo, the second module (a well-regarded one, name like "Tolkenar's ..."), Aid as the group plays it (a fighter gives ST to a wizard; engine only models a self DX boost).
7. Easy-wins handicap idea (computer opponents easier until a character reaches 36 points, plus an IQ rating for wizard opponents): awaiting his go-ahead.

## Owner preferences to remember
One feature at a time; he tests it himself; short answers; he likes more scrolling down over zooming/panning on phones; "fight" not "duel" in wording; wants getting a session going to be easy, especially for him as host.
