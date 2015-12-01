#Project ACTV - Assetto Corsa TV
###Contains:
* Tower (standings - battles)
* Speedtrap
* Driver info (driver change info - qualif time - fastest lap)
* Timer (Session info - Replay)

Driver colors are set with car brand
* bmw-ford: blue
* mercedes-afla romeo: grey
* ruf-corvette-lotus : yellow
* lamborghini-pagani: green

No configurations are possible at the time

maximum amount of cars in the tower is 18

battle ares set at 2.5 sec if nothing 5 sec else standings are shown every lap for 12 sec

works with ac shortcuts (but needs to have onboard camera to pickup the driver change):
* CTRL+1: switch to previous opponent car
* CTRL+3: switch to next opponent car
* CTRL+2: switch to player car

-
###Changelog
0.9.3.0
* fixed ctypes import crashing

0.9.2.0
* another fix for tower in race
* deeper logging and prevent of freezing other widgets in case of an error
* fixed ambiguous file import

0.9.1.0
* added colors for afla romeo(grey),ford(blue)
* fixed online tower - keep alive issue
* nordschleife tourist support
* race standings with validated progress

0.9.0.0
* Initial release

####Todo
* Options
  * maximum number of cars in the tower
  * wether a lap can be invalidated or not (currently hiding lap info)

-
###Installation instructions
1. extract the archive to your assettocorsa folder(...\Steam\steamapps\common\assettocorsa\)
2. In the game's main menu
   * go to Options -> General
   * in the section UI Modules
   * check prunn
3. In game all 4 widgets should appear in the list:
   * ACTV Info, ACTV Timer, ACTV Tower and ACTV Speed Trap
   * if you don't see them at first its normal if they have nothing to show but a mouse over the widget will trigger a background and a title(AC puts them at the top left by default) allowing you to place them as you want
4. don't forget to take a deep breath and smile ;) as you are all set

-
###License
This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.
GNU General Public License v2.
