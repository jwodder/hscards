- Use `basic.json` when generating `cards.txt`
- Remove `$` and `#` prefixes from damage and restored health
- Remove leading "[x]" from card texts?
- Add an option for using a given file as input instead of fetching the data
  from hearthstonejson.com
    - Give the "main" command a `-c <cards-file>` (and, later, `-S
      <strings-file>`) option
- Get enum strings from
  <https://api.hearthstonejson.com/v1/strings/enUS/GLOBAL.json>
- Add an option for including card IDs in spoilers?
- Write a README
- Add `--help` text
- Add docstrings
- Let `checklists` take a list of sets to typeset as arguments

- Checklists:
    - Add an option for whether to include checkboxes?
    - Omit the rarity field from the Basic set checklist
    - Include unlock & golden levels in the Basic set checklist?

- `pdflists.py`:
    - Display the set name somewhere (as a page header?)
    - Recalculate `CARDS_PER_CLASS` for each set (Note that not all classes
      always have the same number of cards; e.g., Hunters in The Grand
      Tournament)
    - Include unlock & golden levels in the Basic set checklist?
    - Fiddle with the bubble-related dimensions
    - Replace the slash with Symbol's \244 (U+2044) ?
    - Replace the circle and star with ZapfDingbats' \155 (U+274D) and \111
      (U+2729 - or U+2606 instead?) ?

- Do something with the following fields?
    - entourage
    - howToEarn
    - howToEarnGolden
    - multiClassGroup
    - faction
    - elite?
    - id?
