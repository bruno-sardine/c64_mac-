# C64 Ultimate TextCreator For the Mac

A Python-based tool for creating and managing formatted text files on the Commodore 64 Ultimate via FTP. This tool allows you to create game documentation (usage notes, tips, and cheats) directly from your Mac, automatically sync them to your C64, and view these notes via the C64U system overlay **while you are within an actively running C64 application**.

### The Necessity / Purpose: 
The C64U is able to either freeze-and-show or slide-over/overlay the system menu on top of the VICII's output .  This allows you to navigate to a .txt file and **view** it in-program! The problem is, The C64U's framework does not have a text editor or creator.  The ultimate goal would be for me to be using a program, such as Easy Script, and **in-program** create a text file that could be used for reminders on the program operation:

```
[Easy Script Commands]
Load: F1 L filename
Save: F1 F filename
View Directory: F4 $0
and so on...
```
By **in-program** I mean not having to exit a game, start up a C64 text editor, load a previously created file, then exiting that, then re-loading your program!  The goal is to achieve creating these notes **outside** of the C64U.  The pictures below clearly illustrate the intention:

![FSII_Cont](https://github.com/user-attachments/assets/df371324-a818-48e9-86b7-35fd30c48c16)

_Figure 1: <kbd>C=</kbd> + <kbd>RESTORE</kbd> > navigate to text file > VIEW "Flight Simulator II_controls.txt"_

![FSII_Tips](https://github.com/user-attachments/assets/397676bf-1c84-4cda-9135-759fffc019d3)

_Figure 2: <kbd>C=</kbd> + <kbd>RESTORE</kbd> > navigate to text file > VIEW "Flight Simulator II_tips.txt"_

## Why Mac-Only?
1. I'm a Mac guy
2. I originally created this in BASH (my favoriate of all langs)
3. Several MacOS BASH/UNIX-y commands simply are not the same as their Linux counterparts (mostly different flags)
4. Why not use FTP and PING?
   - lftp is more command-line friendly, handles paths with spaces better, good timeout control.
   - fping offers parallel scanning (faster than a sequential scan with ping), and has subnet scanning
  
  
## Features

- **Network Auto-Discovery**: Automatically finds your C64 Ultimate device on the network
- **Interactive Text Creation**: Create three types of formatted documentation:
  - **Controls**: Structured key/control documentation with auto-aligned formatting
  - **Usage**: Freeform text for general notes on using a game or program
  - **Tips**: Freeform text for gameplay tips and strategies
  - **Cheats**: Freeform text for cheat codes and secrets
  - **Full Manual**: Freeform text for supplying a full application manual
- **Smart Text Wrapping**: Automatically wraps text to 37 characters for optimal C64 display
- **FTP Integration**: Seamless file upload to C64 Ultimate
- **Directory Management**: Browse and create directories on your C64 Ultimate

## Requirements

### USB Directory Structure
This program is based of of my organizational structure which is as follows:
```
USB1/Favorite Programs/
├── Deadline/
├── Flight Simulator II/
├── Jumpman/
├── MiniFiler/
└── Perry Mason/
```
**Yes, each program get it's own directory.  Why?** 
- Disk space is nearly unlimited.  Why have a single "saves.d64" disk for games like Deadline and Perry Mason, when I can just have a "saves.d64" for Deadline, and a "saves.d64" for Perry Mason?  I also create program specific files, such as a custom .cfg file for Perry Mason.
- This structure allows me to have notes specific for each program (the purpose of this utility).

With these points in mind, my directory structure actually looks like this:
```
USB1/Favorite Programs/
├── Deadline/
│   ├── Deadline.d64
│   ├── Deadline_tips.txt
│   └── saves.d64
├── Flight Simulator II/
│   ├── Flight_Simulator_II.d64
│   └── Flight_Simulator_II_controls.txt
├── Jumpman/
│   ├── jumpman.crt
│   └── jumpman_full_manual.txt
├── MiniFiler/
│   ├── minifiler.d64
│   ├── minifiler_controls.txt
│   └── saves.d64
└── Perry Mason/
    ├── Perry Mason.cfg
    ├── Perry Mason.d64
    └── Perry Mason_hints.txt
```
### Software Dependencies

- Python 3.6 or higher
- `lftp` - FTP client for file transfers
- `fping` - Fast network scanning tool
- macOS (uses `ipconfig` and `arp` commands)

### Install Dependencies

```bash
# Using Homebrew
brew install lftp fping
```

### Hardware Requirements

- Commodore 64 with Ultimate cartridge (Ultimate 64, Ultimate 1541-II, etc.)
- Mac connected to the same network as your C64 Ultimate
- C64 Ultimate configured for FTP access

## Configuration

Edit the configuration section at the top of the script:

```python
ULTIMATE_MAC = "00:00:00:00:00:00"      # Your C64 Ultimate MAC address
INTERFACE = "en1"                       # Your Mac's network interface
REMOTE_PATH_ROOT = "/USB1/Favorite Games"  # Base path on C64 Ultimate
```

### Finding Your Configuration Values

**MAC Address**: Check your C64 Ultimate's network settings or router's device list

**Network Interface**: Run `ifconfig` in terminal to find your active network interface (usually `en0` for Wi-Fi, `en1` for Ethernet)

**Remote Path**: The FTP base directory on your C64 Ultimate where game folders are stored

## Usage

### Starting the Program

```bash
python3 c64.py
```

### Workflow

1. **Network Scan**: The script automatically discovers your C64 Ultimate on the network
2. **Select Directory**: Choose which game folder to save files to, or create a new one
3. **Choose File Type**: Select Controls (1), Usage (2), Tips (3), Cheats (4), or Full Manual (5)
4. **Create Content**: Enter your documentation
5. **Auto-Upload**: File is automatically formatted and uploaded to your C64

### Creating Control Notes

Control notes are perfect for documenting game controls.  This is the **only** option where you must enter KEY/VALUE pairs.  

```
Enter control notes (type '-done-' when finished)
==================================================
Key(s) [or -done-]: F, H
Description: aileron left, right or joystick 1 (on the ground: steering left, right)

Key(s) [or -done-]: B, H
Description: elevator up, down or joystick 1

Key(s) [or -done-]: -done-
```

**Output** (auto-formatted with aligned colons):
```
F, H : aileron left, right or
       joystick 1 (on the ground:
       steering left, right)
B, H : elevator up, down or
       joystick 1
```
Also note, a "controls" document is more about text formatting and less about the actual key strokes.  For example, my "`Hes Games`" control file looks like this:

```
=====================================
HES Games
Controls
-------------------------------------
100M Sprint    : move joystick L/R
110M Hurdle    : move joystick L/R, R
                 to jump
Long Jump      : move joystick L/R,
                 Up to jump, R after
                 landing
```

### Creating Tips, Cheats, Usage, or Manuals

For these items, type freely and the text will be automatically wrapped.  If fact, the code for 4 these elements are exactly the same.  The only difference is the text header that's created (see **File Format**).  It's very easy to simply cut and paste a known piece of text from a wiki or game guide, and let the program take care of word-wrapping:

```
Enter your notes (type '-done-' on its own line when finished)
==================================================
To defeat the final boss, make sure you have collected all power-ups from the secret area in level 3. The boss is vulnerable only during its attack animation.
-done-
```

**Features:**
- Automatic line wrapping at 37 characters
- Tab characters converted to 4 spaces
- Preserves paragraph breaks (blank lines)
- Type `-done-` on its own line to finish

## File Format

All created files include a formatted header:

```
=====================================
<Program Name>
<Controls | Usage | Tips | Cheats | Full Manual>
-------------------------------------
[Your content here]
```

Files are named automatically: `GameName_controls.txt`, `GameName_tips.txt`, `GameName_cheats.txt`, etc and pushed to the the same directory as the program.

## Menu Options

### Main Directory Menu

- **1-N**: Select numbered directory
- **r**: Refresh/Re-scan IP (forces full network scan)
- **c**: Create new directory
- **q**: Quit program

### Creating Directories

This is usefull for when you already have a program scatterd on the file system (e.g. `Spy vs Spy.crt`) and you wish to organize it.  

- Maximum 27 characters (C64 display constraint)
- Spaces are allowed in directory names
- Type `cancel` to abort directory creation

Using the Spy vs Spy example, workflow would be:
1. Create a directory called "Spy vs Spy"
2. Choose the number for the newly created `Spy vs Spy` directory
3. Create a guide.  For example, perhaps a "Usage" guide to decribe what all of the weapons do.
4. On the C64U, copy `Spy vs Spy.crt` to the newly created "`Spy vs Spy`" directory.  You will now have this structure:
   ```
   USB1/Favorite Programs/
    ├── Spy vs Spy/
    │   ├── Spy vs Spy.crt
    │   ├── Spy vs Spy_usage.txt

    ```

## Troubleshooting

### "Could not find C64U at [MAC address]"

- Verify your C64 Ultimate is powered on and connected to the network
- Check that the MAC address in the configuration is correct
- Ensure your Mac and C64 are on the same network subnet
- Try pressing 'r' to force a full network scan

### "Connection lost" or FTP Errors

- Verify FTP is enabled on your C64 Ultimate
- Check the `REMOTE_PATH_ROOT` setting matches your C64's directory structure
- Ensure no firewall is blocking FTP traffic (port 21)

### Network Interface Issues

- Run `ifconfig` to verify your network interface name
- Update the `INTERFACE` setting if needed
- Common values: `en0` (Wi-Fi), `en1` (Ethernet)

### Slow Network Scans

The first scan may take 10-15 seconds as it scans the entire subnet. Subsequent scans use the ARP cache and complete instantly. Press 'r' only if you need to force a full rescan (e.g., if the C64's IP changed).

## Technical Details

### Text Formatting

- **Line Width**: 37 characters (optimal for C64 40-column display)
- **Notes**: Automatic colon alignment based on longest key name
- **Wrapping**: Uses Python's `textwrap` with smart word breaking
- **Character Handling**: Tabs converted to 4 spaces, compatible with PETSCII

### Network Discovery

1. Checks ARP cache first (instant if device was recently seen)
2. Falls back to `fping` subnet scan if not cached
3. Caches discovered IP for session duration
4. 'r' option forces fresh scan bypassing cache

### File Storage

- Temporary files created in `/tmp/` directory
- Files automatically uploaded via FTP
- No local copies retained (everything goes to C64)

## Contributing

Contributions are welcome! Areas for potential improvement:

- Support for other platforms (Linux, Windows)
- Additional file format options
- Batch file processing
- Configuration file support

## Windows Support

This tool was designed for macOS but can be adapted for Windows with the following modifications:

### Required Changes

**1. Command Replacements**
- `ipconfig getifaddr` → `ipconfig` (parse output differently)
- `arp -an -i INTERFACE` → `arp -a` (Windows doesn't use `-i` flag)
- File paths: `/tmp/` → `%TEMP%` or `C:\Users\USERNAME\AppData\Local\Temp\`

**2. Windows-Specific Tools**
- **fping**: Not natively available. Options:
  - Use `nmap` instead: `nmap -sn 192.168.1.0/24`
  - Use PowerShell: `1..254 | ForEach-Object {Test-Connection "192.168.1.$_" -Count 1 -Quiet}`
  - Install `fping` via Cygwin or WSL
- **lftp**: Not natively available. Options:
  - Install via Cygwin
  - Install via Windows Subsystem for Linux (WSL)
  - Use WinSCP command-line interface as alternative
  - Use Python's `ftplib` library (rewrite FTP functions)

**3. Network Interface Discovery**
- Windows uses different interface naming (e.g., "Ethernet", "Wi-Fi")
- Use `ipconfig /all` to find interface names
- Parse output to extract IP and interface information

**4. Path Handling**
- Replace `Path.home()` usage with Windows-compatible paths
- Use `pathlib.Path` (already used) which handles Windows paths
- Change temp directory from `/tmp/` to `Path(tempfile.gettempdir())`

### Windows Installation Options

**Option 1: WSL (Windows Subsystem for Linux)** - Recommended
- Install WSL2
- Run the script unmodified in Linux environment
- All tools available via `apt install lftp fping`

**Option 2: Native Windows Port**
- Install Python 3.6+
- Install Cygwin with `lftp` and `fping` packages
- Modify script to use Windows commands
- Add Cygwin to PATH

**Option 3: Python-Only Rewrite**
- Replace `lftp` with Python's `ftplib`
- Replace `fping` with Python socket programming
- Replace system calls with cross-platform alternatives
- Most portable but requires significant rewrite


**Pull requests welcome** for a fully Windows-compatible version!


