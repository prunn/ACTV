#Project ACTV - Assetto Corsa TV
###Contains:
* Tower (standings - battles)
* Speedtrap
* Driver info (driver change info - qualif time - fastest lap)
* Timer (Session info - Replay)
* Config (Configuration)

Driver colors are set with car brand
* bmw-ford-shelby: blue
* mercedes-mazda: grey
* ruf-corvette-lotus : yellow
* lamborghini-pagani: lime-green
* alpha romeo: forest-green
* nissan: purple
* ktm-mclaren: orange

battle ares set at 2.5 sec if nothing 5 sec else standings are shown every lap for 12 sec

-
###Changelog
1.2.0
Fixed over 30 mins timed races
Improved tower display for 1st lap of race
Tower highlight on current car instead of driver only
Pit window open/close message
Tower qualif : Forcing to show full time instead of gaps when highlighted
Tower faded dnf drivers
Info widget resizing depending on driver name length

1.1.1
Customizable Theme Color Base (RGB)
Config qualif new lap color(Red-Green)
Tower : detection if pitstop or respawned in pits
Timed races support

1.1.0
code optimisation
fetching times from server when joining online session(practise,qualif)
added delta widget
Tower: gained/lost position triangle
Tower: cars finishing laps down
Speedtrap: stays on a little longer

1.0.0
yellow timer flag
name in tower is yellow when stopped on track
changed hotkey(mode change) to ctrl+d
last laptime is shown for full tower with gaps in race(5 sec purple for personal best,red for slower)
scrolling effect for tower in race(top 3 always shown, then driver remains displayed whatever the maximum number of driver shown in config)
added colors for nissan(purple),ktm/mclaren(orange),alpha romeo(forest green)
replay beta working on practice qualify sessions

0.9.6
Config : base row height
Removed pinhack option and code(not needed anymore)
Full tower with gaps - PIT and DNF(for player disconnected)
Reworked animations - implemented in label class
added pitlane indicator for qualif/practice
added new fonction from AC 1.5 api
added tower: click to view driver

0.9.5
config window
full tower race mode
gaps or laps for qualif/practise
hotkey f7 to change mode

0.9.4
bug fixes
stint view
speed units bounded to game options

0.9.3
* fixed ctypes import crashing

0.9.2
* another fix for tower in race
* deeper logging and prevent of freezing other widgets in case of an error
* fixed ambiguous file import

0.9.1
* added colors for afla romeo(grey),ford(blue)
* fixed online tower - keep alive issue
* nordschleife tourist support
* race standings with validated progress

0.9.0
* Initial release

####Todo

-
###Installation instructions
1. extract the archive to your assettocorsa folder(...\Steam\steamapps\common\assettocorsa\)
2. In the game's main menu
   * go to Options -> General
   * in the section UI Modules
   * check prunn
3. In game all 4 widgets should appear in the list:
   * ACTV Info, ACTV Timer, ACTV Tower, ACTV Speed Trap and ACTV Config
   * if you don't see them at first its normal if they have nothing to show but a mouse over the widget will trigger a background and a title(AC puts them at the top left by default) allowing you to place them as you want
4. don't forget to take a deep breath and smile ;) as you are all set

-
###License
This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.
GNU General Public License v2.
