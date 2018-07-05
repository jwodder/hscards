- Get enum strings from
  <https://api.hearthstonejson.com/v1/strings/enUS/GLOBAL.json>
    - Give the "main" command an `-S <strings-file>` option
- Add docstrings
- Make sure the code can handle being given a list of all cards (not just
  collectibles) as input
- Add an option for specifying what language to fetch files for

- Spoilers:
    - Include unlock levels from `basic.json`

- Checklists:
    - Let `checklists` take a list of sets to typeset as arguments
    - Add an option for whether to include checkboxes?
    - Omit the rarity field from the Basic set checklist
    - Include unlock & golden levels in the Basic set checklist?
    - Add an option for naming the files after the sets' full names rather than
      enum names
    - PDF format:
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
