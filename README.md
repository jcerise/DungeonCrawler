DungeonCrawler
==============

A simple rogue-like game written in Python.

Uses the libtcodpy library.

Currently, the game consists of a random map generator, line of sight, movement, random monster placement based on
leveled lists, random placement of some items based on leveled lists, and attack mechanics.

Content is slowly being added, so please realize this is a work in progress.

Magic is currently only implemented in the form of magic scrolls that can be found and used as items. The player
has no latent magical abilities, although this will be added in the near future. Monsters are all also very, very, weak.
This is more for testing purposes, and will be balanced out as the game progresses.

Running the code
----------------

To run DungeonCrawler, you first need to make sure you have Python 2.7.3 installed. This currently will not
work with Python 3.

Download the code somewhere, unzip/tar it, cd into the directory and run

```
python DungeonCrawler.py
```

Currently known to work on Windows and Linux, and *probably* Mac (needs testing, I don't own a Mac).

Controls
-----------------

+ LAlt + Enter = Fullscreen mode
+ Escape = Exit
+ Arrow Keys = Move
+ i = Open Inventory
+ a..z = When in inventory screen, use item at index [char]
+ g = pick up item currently under player
+ Mouse = Identify object under pointer, target tile under pointer (for some spells, items)

To attack, simply move into the object your target
