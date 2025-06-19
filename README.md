# 0xAC – Version 1.0

<p align="center">  
  <img src="https://github.com/catab60/0xAC/blob/main/assets/logo.gif?raw=true", width="1000">  
</p>  

This is an **AssaultCube** memory‑manipulation hack built entirely in Python, leveraging the [`pymem`](https://github.com/Srounet/Pymem) library to read and write process memory. It offers a suite of powerful cheats and was created as a challenge to master memory hacking in a high‑level language—a crash course that proved both tough and incredibly rewarding.

## About the Project

[![Alt text](https://img.youtube.com/vi/Om8iG21hER4/0.jpg)](https://www.youtube.com/watch?v=Om8iG21hER4)

This **Version 0.1** hack injects into AssaultCube’s process using `pymem`, dynamically scanning for pointers and patching memory at runtime to give you god‑mode and advanced cheats. Written as a learning exercise, it demonstrates how you can manipulate another process’s memory with pure Python and a dedicated library.

## Features

* **Infinite Mods**

  * Infinite Health & Armor
  * Infinite Ammo & Grenades
* **Combat Enhancements**

  * Rapid Fire
  * No Recoil
* **Aiming & Detection**

  * Aimbot (auto-lock with optional smoothing)
  * ESP (see enemies through walls with distance and health overlays)
* **Fun Mode**

  * Custom visual effects to spice up the battlefield

## Keyboard Shortcuts

* **LSHIFT**: Open/close the overlay menu
* **↑ ↓ ← →**: Navigate the menu options
* **Enter**: Toggle the selected feature on/off

## Future Improvements

* **Config File Support**: Save/load favorite presets
* **Customizable Hotkeys**: Let users bind their own keys
* **Cross‑Platform Compatibility**: Bring support to Linux and macOS

## Usage Guide

1. **Clone the repository**

   ```bash
   git clone https://github.com/catab60/0xAC.git
   cd 0xAC
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt  
   ```

3. **Run the hack**

   ```bash
   python main.py  
   ```

4. **In‑Game Controls**

   * Press **LSHIFT** to open the hack menu
   * Navigate with the **arrow keys**
   * Press **Enter** to toggle a cheat


## Learning Experience

This project was a deep dive into process memory manipulation using Python’s `pymem` (built on `ctypes`/`pywin32`). Tackling pointer arithmetic, dynamic address scanning, and threading in a high‑level language was challenging but provided invaluable insights into how games manage data in memory and how one can interface with it safely (or unsafely!).

### Contributions

Feel free to fork the repo to suggest new cheats, optimize performance, or add cross‑platform support. Pull requests and issue reports are very welcome!

---

⚠️ **Disclaimer:** For educational purposes only. Modifying or distributing cheats for online play may violate game terms of service, use responsibly.
