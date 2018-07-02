- Use `basic.json` when generating `cards.txt`
- Remove `$` and `#` prefixes from damage and restored health
- Remove leading "[x]" from card texts?
- Add options for only creating the spoilers or checklists but not both
- Add an option for using a given file as input instead of fetching the data
  from hearthstonejson.com
- Get enum strings from
  <https://api.hearthstonejson.com/v1/strings/enUS/GLOBAL.json>

- Checklists:
    - Add an option for setting the output directory/output path
    - Add an option for whether to include checkboxes?
    - Omit the rarity field from the Basic set checklist
    - Include unlock & golden levels in the Basic set checklist?

- `pdflists.py`:
    - Add an option for setting the output directory
    - Display the set name somewhere
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
