- Get enum strings from
  <https://api.hearthstonejson.com/v1/strings/enUS/GLOBAL.json>
    - Give the "main" command an `-S <strings-file>` option
- Add docstrings
- Make sure the code can handle being given a list of all cards (not just
  collectibles) as input
- Add an option for specifying what language to fetch files for

- Checklists:
    - Add an option for whether to include checkboxes?
    - Include unlock & golden levels in the Basic set checklist?
    - PDF format:
        - Display the set name somewhere (as a page header?)
        - Recalculate `CARDS_PER_CLASS` for each set (Note that not all classes
          always have the same number of cards; e.g., Hunters in The Grand
          Tournament)
        - Fiddle with the bubble-related dimensions
        - Replace the slash with U+2044?

- Do something with the following fields?
    - entourage
    - howToEarn
    - howToEarnGolden
    - multiClassGroup
    - faction
    - elite?
    - id?
