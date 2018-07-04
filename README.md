This is a script for generating text spoilers and set checklists for
[Hearthstone](https://playhearthstone.com).

Installation & Running
======================

Python 3.6 or higher is required.

1. Copy/clone the code to your computer

2. In this directory, run `python3 -m pip install --user -r requirements.txt`
   (Requires [pip](https://pip.pypa.io))

3. Run the code by running `python3 -m hscards ...` in this directory.  (There
   are other possible ways to run the code, but let's just stick to one simple
   method here.)

Usage
=====

By default, all commands fetch card data from <https://hearthstonejson.com> —
specifically,
<https://api.hearthstonejson.com/v1/latest/enUS/cards.collectible.json>.  The
`c`/`--cards-file` option can be used to specify a different file or URL in the
same format to use instead.

`spoiler` command
-----------------

    python -m hscards [-c <cards-file>] spoiler [-o <outfile>]

Generate a file of text spoilers for all collectible Hearthstone cards.  The
spoilers look like this:

    Name:   Explosive Trap
    Type:   Spell — Secret
    Cost:   2
    Class:  Hunter
    Text:   <b>Secret:</b> When your hero is attacked, deal 2 damage to all
              enemies.
    Set:    Classic (Common)
    Flavor: It traps your food AND cooks it for you!
    Artist: Brandon Kitkouski

By default, the spoilers are written to `cards.txt`; the `-o`/`--outfile`
option can be used to specify a different file.

`checklists` command
--------------------

    python -m hscards [-c <cards-file>] checklists [-d <output-dir>] [-f <txt|pdf>]

Generate checklists for each collectible Hearthstone card set, one file per
set.  Files are created in the directory specified with the `-d`/`--output-dir`
option (default: `checklists`) and are named with each set's internal codename
(e.g., the Basic set is `CORE.txt` and the Classic set is `EXPERT1.txt`).  The
checklist file format can be set with the `-f`/`--format` option: either `txt`
(the default) or `pdf`.
