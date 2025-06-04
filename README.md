# Rampage Arcade (MCR-3) Disassembly Project

## Introduction

This repository documents a mostly detailed disassembly and technical study of the Z80 program ROM for **Rampage** (Bally Midway, 1986), a classic arcade game running on the MCR-3 hardware platform. The purpose of this project is to provide a comprehensive, annotated look at the game’s code for **educational and historical purposes**.

Rampage is notable for its multiplayer action, creative design, and its use of advanced arcade hardware. By making the internal structure and logic of the game accessible, this project aims to help future generations of programmers, hobbyists, and researchers understand how these iconic systems were engineered.

## What’s Included

- **Mostly commented Z80 assembly source**, covering startup, sound handling, input processing, sprite display logic, level decoding, and hardware interfacing.
- **Hardware interface notes** for the MCR-3 platform (I/O ports, watchdog handling, sound board protocol, etc.).
- **Detailed explanations** of key routines, including initialization, menu input debounce, sound handshaking, and more.
- **Historical commentary** on programming practices of the 1980s arcade era.

## Who Is This For?

- Retro programmers and reverse engineers  
- Video game historians and preservationists  
- Anyone interested in how arcade games worked “under the hood”

## Why Disassemble?

- To **preserve** knowledge of classic game design and hardware integration
- To **educate** others about vintage software engineering techniques
- To provide a technical reference for related MCR-3 hardware games

- ## Generating Rampage Graphics from Original ROMs

This project includes a batch file, `convert_data.bat`, which automates the process of extracting and converting Rampage’s graphical data into viewable images.

### Requirements

- Python 3
- Pillow Python library (`pip install Pillow`)
- The original Rampage arcade ROM files (not included)

### Usage

1. Unzip the Rampage ROM files in the same directory as `convert_data.bat` and the Python scripts.
2. Run `convert_data.bat` by double-clicking it or executing it from the command line.
3. The script will generate many PNG images for tiles, backgrounds, and sprites. These generate folders PNG, MAPS, LEVELS_PNG

The output images will provide a complete visual reference to all major graphics used in the original arcade game.

*Note: Only the extraction/conversion scripts are included here. You must supply your own legally obtained ROMs.*


## Legal Notice

This project does **not** include any original Rampage ROM data or copyrighted
audio/graphic assets.  
All disassembly and annotations are the result of independent reverse engineering, using only **publicly available tools** and **personally dumped ROM images**.

If you are a rights holder and believe any material should be removed, please contact me via GitHub and I will **promptly comply**.

## Disclaimer

- This project is for **non-commercial, educational, and historical use only**.
- Redistribution of original ROM data or copyrighted assets is **not permitted**.
