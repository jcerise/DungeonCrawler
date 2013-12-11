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
+ Escape = Exit (Game is auto saved on exit, Only one save may exist at a time)
+ Arrow Keys = Move
+ i = Open Inventory
+ d = Open Drop menu (selected item is dropped from inventory)
+ c = View Character information
+ e = Examine an item
+ > = Go down stairs (when directly on top of stairs)
+ a..z = When in inventory screen, use item at index [char]
+ g = pick up item currently under player
+ Mouse = Identify object under pointer, target tile under pointer (for some spells, items)

To attack, simply move into your target

To equip items you find along your journey (swords, shields, armor etc) open the inventory, and use the equipment like
any other item

Licensed under the Free BSD License
-----------------------------------

Copyright (c) 2013, Jeremy Cerise
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions and the following
disclaimer.

Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
disclaimer in the documentation and/or other materials provided with the distribution.

Neither the name of the author nor the names of its contributors may be used to endorse or promote products
derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/jcerise/dungeoncrawler/trend.png)](https://bitdeli.com/free "Bitdeli Badge")

