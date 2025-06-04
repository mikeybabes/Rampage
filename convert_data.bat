@echo off
REM this Daddy size batch files will produce a bucklet load of data & PNGs for your viewing pleasure
REM join the two 32k ROM into one binary technically no need but just easier

IF NOT EXIST "pro-0_3b_rev_3_8-27-86.3b" (
    echo You must provide unzip the rampage.zip roms her for anything to work! Exiting.
    exit /b 1
)

echo Looks like you got at least the roms. Let's get cracking.

copy /b pro-0_3b_rev_3_8-27-86.3b+pro-1_5b_rev_3_8-27-86.5b cpu.bin

REM the rom palettes are a nightmare format, so we cheat and use mame ones. Supplied
REM after many hours to trying to work out how the palettes actually correctly match what mame has was beyond my know howw
REM even reading the old mame source files it just couldn't get same values/

REM Old method which look too long
python python\merge_mcr3_bg_4bp.py bg-0_u15_7-23-86.15a bg-1_u14_7-23-86.14b GFX2.BIN --xor FF

REM now use simpler merge nybble function
python python\merge2bits.py bg-0_u15_7-23-86.15a bg-1_u14_7-23-86.14b background4bits.bin
python python\swap_nybble.py background4bits.bin background.bin FF
REM now we end up with BG-REV.bin this is perfect for our needs
python python\swap_nybble.py background.bin BG-REV.bin
REM let's plot a test image of the characters
python python\characters_grid.py  background.bin mame.pal characters.png

REM Decompress some of the background assets and title screen images

python python\decomp.py cpu.bin MAPS\title_screen_81c6.bin 81C6
python python\decomp.py cpu.bin MAPS\ge-li-ra_select_screen.bin 8637
python python\decomp.py cpu.bin MAPS\road_strip_78A0.bin 78A0
python python\decomp.py cpu.bin MAPS\road_with_water_gap_left_79c9.bin  79C9
python python\decomp.py cpu.bin MAPS\road_with_water_gap_right_79aa.bin 79AA
python python\decomp.py cpu.bin MAPS\silhouette1_7c45.bin 7C45
python python\decomp.py cpu.bin MAPS\silhouette2_79e8.bin 79E8
python python\decomp.py cpu.bin MAPS\silhouette3_763e.bin 763E
python python\decomp.py cpu.bin MAPS\silhouette4_7ee3.bin 7EE3
python python\decomp.py cpu.bin MAPS\silhouette5_7f91.bin 7F91
python python\decomp.py cpu.bin MAPS\train_track_78f7.bin 78F7
python python\decomp.py cpu.bin MAPS\water_piers1_78fe.bin 78FE
python python\decomp.py cpu.bin MAPS\water_piers2_7956.bin 7956
python python\decomp.py cpu.bin MAPS\dateline.map 6dc7
python python\decomp.py cpu.bin MAPS\dateline_george.map 6ee1
python python\decomp.py cpu.bin MAPS\dateline_lizzie.map 7038
python python\decomp.py cpu.bin MAPS\dateline_ralph.map 7189
REM This is plotted at each level, to clear top 3 lines. Score and status info.
python python\decomp.py cpu.bin MAPS\score-area.bin 7613

python python\savebit2.py cpu.bin MAPS\trees1_9AEE.bin 9AEE 9B6E
python python\tile_plot.py BG-REV.bin palettes_1.pal MAPS\trees1_9AEE.bin PNG\trees_and_grass1.png

python python\savebit2.py cpu.bin MAPS\trees2_9B6E.bin 9B6E 9C2E
python python\tile_plot.py BG-REV.bin palettes_1.pal MAPS\trees2_9B6E.bin PNG\trees_and_grass2.png

python python\savebit2.py cpu.bin MAPS\trees3_9AEE.bin 9AEE 9B6E
python python\tile_plot.py BG-REV.bin palettes_1.pal MAPS\trees1_9AEE.bin PNG\trees_and_grass1.png

python python\savebit2.py cpu.bin MAPS\snow_ground_9C2E.bin 9C2E 9CAE
python python\tile_plot.py BG-REV.bin palettes_1.pal MAPS\snow_ground_9C2E.bin PNG\trees_and_snow.png

python python\savebit2.py cpu.bin MAPS\cactus_9CAE.bin 9CAE 9D2e
python python\tile_plot.py BG-REV.bin palettes_1.pal MAPS\cactus_9CAE.bin PNG\cactus_desert.png


REM this generates every building image in the game as a PNG file
python python\building_plot_multi.py BG-REV.bin palettes_1.pal cpu.bin 95b6 PNG\Buildings.png


REM turn them into PNG files to look @
REM Palette 1 is main game palette, palette_2 is home title page, palette_3 is news screen
python python\tile_plot.py BG-REV.bin palettes_2.pal MAPS\title_screen_81c6.bin PNG\Title_Screen.png
python python\tile_plot.py BG-REV.bin palettes_1.pal MAPS\ge-li-ra_select_screen.bin PNG\george-lizzie-ralph1.png

python python\tile_plot.py BG-REV.bin palettes_1.pal MAPS\road_strip_78A0.bin PNG\road.png
python python\tile_plot.py BG-REV.bin palettes_1.pal MAPS\road_with_water_gap_left_79c9.bin PNG\water_side1.png
python python\tile_plot.py BG-REV.bin palettes_1.pal MAPS\road_with_water_gap_right_79aa.bin PNG\water_side2.png
python python\tile_plot.py BG-REV.bin palettes_1.pal MAPS\silhouette1_7c45.bin PNG\silhouette1.png
python python\tile_plot.py BG-REV.bin palettes_1.pal MAPS\silhouette2_79e8.bin PNG\silhouette2.png
python python\tile_plot.py BG-REV.bin palettes_1.pal MAPS\silhouette3_763e.bin PNG\silhouette3.png
python python\tile_plot.py BG-REV.bin palettes_1.pal MAPS\silhouette4_7ee3.bin PNG\silhouette4.png
python python\tile_plot.py BG-REV.bin palettes_1.pal MAPS\silhouette5_7f91.bin PNG\silhouette5.png
python python\tile_plot.py BG-REV.bin palettes_1.pal MAPS\train_track_78f7.bin PNG\train_track.png
python python\tile_plot.py BG-REV.bin palettes_1.pal MAPS\water_piers1_78fe.bin PNG\water1.png
python python\tile_plot.py BG-REV.bin palettes_1.pal MAPS\water_piers2_7956.bin PNG\water2.png
python python\tile_plot.py BG-REV.bin palettes_3.pal MAPS\dateline.map PNG\dateline.png
python python\tile_plot.py BG-REV.bin palettes_3.pal MAPS\dateline_george.map PNG\dateline_george.png
python python\tile_plot.py BG-REV.bin palettes_3.pal MAPS\dateline_lizzie.map PNG\dateline_lizzie.png
python python\tile_plot.py BG-REV.bin palettes_3.pal MAPS\dateline_ralph.map PNG\dateline_ralph.png


REM now let's make up the sprites binary from rom files.
python python\merge-binary.py fg-0_8e_6-30-86.8e fg-1_6e_6-30-86.6e fg-2_5e_6-30-86.5e fg-3_4e_6-30-86.4e sprites.bin

REM now we put the sprites into a normal linear format as 4bits / pixels 32x32 pixels
python python\swapnybbles.py sprites.bin

REM let's make a cool reference grid for all sprites you can turn off gride change width as you like
python python\sprite_grid_plot.py sprites.bin mame.pal All_Rampage_sprites_Indexed.png --number --width 16

REM Now this generates the entire game level data into one folder LEVELS_PNG.
REM you can use optional paramaters like --level for a particular level number, or --levels count for so many to process, also also there is a --grid which put a 1pixel divider to show each level.

REM we use the rom binary, combined characters in linear format. (makes it easier), level game palette.
python python\level_generator_final.py cpu.bin bg-rev.bin palettes_1.pal LEVELS_PNG\Game_level

REM This will make up a giant PNG with all the Levels the --number shows the level number visually top middle
REM the --grid gives a 1pixel outline for the area.
python python\grid_pngs.py LEVELS_PNG All_Levels.png --number --grid

REM Sprites as a strip of three, as stored in tables inside game disassembly this shows you how the makeup of the game sprites is done
REM each player sprites is two 2x2 32x32pixel sprites which is big! the sprites are overlapped in an adjusted space
REM also a few special conditions will move say the punch sprite you can see which easily outside with a hand coded x y offset condition for that player action.
python python\compose_rampage_sprite_reverse.py cpu.bin sprites.bin palettes_1.pal Players_sprites.png

REM now we spice it up a litte, we read a entire set of sprite pairs in a text file I've called it sprite_pairs.txt
REM this is the take number offsets shown in the Player_sprites_tables_info.png.
REM Now there are some strange conditions which is handled seperatly in the code for offset of some sprites like the punches, this needs to be treated seperate, as the control logic is a little more complicated
REM Someone else may pick up the challenge to be bothered to fix the positions, but I am not python expert so "Sal la vie"
python python\compose_rampage_overlay_pairs_space.py cpu.bin sprites.bin palettes_1.pal sprite_pairs.txt Players_sprites.png --gapy 32
Del *.bin
REM if you have questions and no spam email me mikeybabes@gmail.com

