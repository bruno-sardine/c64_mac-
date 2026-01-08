#!/usr/bin/env python3
"""
C64 Ultimate File Manager
Creates formatted text files and syncs them to C64 Ultimate via FTP
"""

import subprocess
import textwrap
from pathlib import Path
import re
import sys
import threading
import time

# --- CONFIGURATION ---
ULTIMATE_MAC = "2:15:41:7e:44:32"  # MAC address of C64 Ultimate device
INTERFACE = "en1"                   # Network interface to scan
REMOTE_PATH_ROOT = "/USB1/Favorite Games"  # Base path on C64 Ultimate

# Global variable to cache the discovered IP address
TARGET_IP = ""

def find_ultimate_ip(force_scan=False):
    """
    Scan network for C64 Ultimate device.
    
    Args:
        force_scan: If True, skip ARP cache and force a full network scan
        
    Returns:
        bool: True if device found, False otherwise
    """
    global TARGET_IP
    
    print("Scanning network for C64 Ultimate...")
    
    # Get local IP address for this interface
    try:
        result = subprocess.run(
            ["ipconfig", "getifaddr", INTERFACE],
            capture_output=True,
            text=True,
            check=True
        )
        my_ip = result.stdout.strip()
    except subprocess.CalledProcessError:
        print(f"Error: Could not get IP for interface {INTERFACE}")
        return False
    
    # Extract subnet (e.g., "192.168.1" from "192.168.1.100")
    subnet = ".".join(my_ip.split(".")[:3])
    
    # Prepare MAC address for searching (remove leading zeros if present)
    search_mac = ULTIMATE_MAC.lstrip("0")
    
    # Only check ARP cache if not forcing a full scan
    if not force_scan:
        print("Checking ARP cache...")
        try:
            result = subprocess.run(
                ["arp", "-an", "-i", INTERFACE],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Search through ARP table for our MAC address
            for line in result.stdout.split("\n"):
                if search_mac.lower() in line.lower():
                    # Extract IP from format: hostname (192.168.1.x) at ...
                    match = re.search(r'\(([0-9.]+)\)', line)
                    if match:
                        TARGET_IP = match.group(1)
                        print(f"Found Commodore 64 Ultimate at: {TARGET_IP} (cached)")
                        return True
        except subprocess.CalledProcessError:
            pass
    
    # ARP cache miss or forced scan - run fping to discover device
    print("Not in ARP cache, scanning subnet..." if not force_scan else "Performing full network scan...")
    subprocess.run(
        ["fping", "-I", INTERFACE, "-aqg", f"{subnet}.0/24"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    # Search ARP table again after fping populates it
    try:
        result = subprocess.run(
            ["arp", "-an", "-i", INTERFACE],
            capture_output=True,
            text=True,
            check=True
        )
        
        for line in result.stdout.split("\n"):
            if search_mac.lower() in line.lower():
                match = re.search(r'\(([0-9.]+)\)', line)
                if match:
                    TARGET_IP = match.group(1)
                    print(f"Found Commodore 64 Ultimate at: {TARGET_IP}")
                    return True
    except subprocess.CalledProcessError:
        pass
    
    print(f"Error: Could not find C64U at {ULTIMATE_MAC}")
    return False

def get_remote_directories():
    """
    Fetch list of directories from C64 Ultimate via FTP.
    
    Returns:
        list: List of directory names, or None if connection failed
    """
    cmd = f'lftp -c "set net:timeout 5; open ftp://{TARGET_IP}; ls {REMOTE_PATH_ROOT}"'
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10,
            check=True
        )
        
        # Parse directory lines (lines starting with 'd' are directories)
        dirs = []
        for line in result.stdout.split("\n"):
            if line.startswith('d'):
                # Extract directory name from last field(s) of ls output
                parts = line.split()
                if len(parts) >= 9:
                    # Join all parts from index 8 onwards (handles names with spaces)
                    dirs.append(" ".join(parts[8:]))
        
        return dirs
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None

def select_remote_dir():
    """
    Interactive directory selection with options to refresh or create new.
    
    Returns:
        tuple: (directory_name, full_remote_path) or None if failed
    """
    global TARGET_IP
    
    # Ensure we have a valid IP address
    if not TARGET_IP:
        if not find_ultimate_ip():
            return None
    
    print("Fetching directory list...")
    dirs = get_remote_directories()
    
    # Handle connection failure
    if dirs is None:
        print("Connection lost. Re-scanning IP...")
        TARGET_IP = ""
        if find_ultimate_ip():
            return select_remote_dir()
        return None
    
    # Display menu
    #print("-" * 40)
    print("\033[38;5;208m" + "-" * 40 + "\033[0m")
    for i, dirname in enumerate(dirs, 1):
        print(f"{i}. {dirname}")
    #print("r. Re-scan IP / Refresh")
    #print("c. Create directory")
    #print("q. Quit Script")
    print("\033[34mr. Re-scan IP / Refresh\033[0m")
    print("\033[34mc. Create directory\033[0m")
    print("\033[34mq. Quit Script\033[0m")
    #print("-" * 40)
    print("\033[38;5;208m" + "-" * 40 + "\033[0m")
    
    choice = input("Select Folder or Command: ").strip()
    
    # Handle menu options
    if choice.lower() == "q":
        exit(0)
    elif choice.lower() == "c":
        # Create new directory then refresh the list
        if create_remote_directory():
            return select_remote_dir()
        else:
            return select_remote_dir()
    elif choice.lower() == "r":
        # Clear cached IP and force a full network scan
        TARGET_IP = ""
        if find_ultimate_ip(force_scan=True):
            return select_remote_dir()
        return None
    
    # Try to parse numeric selection
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(dirs):
            selected = dirs[idx]
            remote_path = f"{REMOTE_PATH_ROOT}/{selected}"
            print(f">>> Syncing to: {remote_path}")
            return selected, remote_path
    except (ValueError, IndexError):
        pass
    
    print("Invalid selection")
    return select_remote_dir()

def create_remote_directory():
    """
    Prompt user to create a new directory on C64 Ultimate.
    Validates length constraints and handles spaces in names.
    
    Returns:
        bool: True if directory created successfully, False otherwise
    """
    while True:
        dir_name = input("\nEnter name for new directory (or 'cancel' to exit): ").strip()

        # Allow user to cancel operation
        if dir_name.lower() == 'cancel':
            print("Operation cancelled.")
            return False

        # Validate directory name isn't empty
        if not dir_name:
            print("--> Error: Directory name cannot be empty.")
            continue

        # Validate length for C64/Ultimate display constraints
        if len(dir_name) > 27:
            print(f"--> Error: '{dir_name}' is {len(dir_name)} characters.")
            print("--> Please use 27 or fewer characters for proper directory listing.")
            continue
        
        # Attempt to create directory via FTP
        full_path = f"{REMOTE_PATH_ROOT}/{dir_name}"
        cmd = f'lftp -c "set net:timeout 5; open ftp://{TARGET_IP}; mkdir \\"{full_path}\\""'
        
        try:
            subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10,
                check=True
            )
            print(f"Successfully created directory: {dir_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Failed to create directory. The folder might already exist.")
            return False
        except subprocess.TimeoutExpired:
            print("Connection timed out. Check your network connection.")
            return False

def create_control_notes(max_width=37):
    """
    Interactive creation of formatted usage/controls documentation.
    Prompts for key/button and description pairs, then formats with aligned colons.
    
    Args:
        max_width: Maximum line width in characters (default 37 for C64 display)
        
    Returns:
        str: Formatted text with aligned entries, or None if no entries
    """
    entries = []
    max_key_len = 0
    
    print("\nEnter Control Reference notes (type '-done-' when finished)")
    print("=" * 59)
    
    # Collect all key/description pairs
    while True:
        key = input("Key(s) [or -done-]: ").strip()
        if key.lower() == "-done-":
            break
        
        if not key:
            continue
        
        desc = input("Description: ").strip()
        
        entries.append((key, desc))
        max_key_len = max(max_key_len, len(key))
    
    if not entries:
        return None
    
    # Format output with aligned colons
    output_lines = []
    indent_width = max_key_len + 3  # Space for " : " (space + colon + space)
    
    for key, desc in entries:
        # Calculate padding needed to align all colons
        padding = " " * (max_key_len - len(key))
        
        # Create first line: "KEY     : description"
        first_line = f"{key}{padding} : {desc}"
        
        # Wrap at max_width, indenting continuation lines to align after colon
        wrapped = textwrap.wrap(
            first_line,
            width=max_width,
            subsequent_indent=" " * indent_width,
            break_long_words=False,
            break_on_hyphens=False
        )
        
        output_lines.extend(wrapped)
    
    return "\n".join(output_lines)

def create_freeform_notes(max_width=37):
    """
    Interactive freeform text entry with automatic wrapping.
    User types freely until entering "-done-" on its own line.
    
    Args:
        max_width: Maximum line width in characters (default 37 for C64 display)
        
    Returns:
        str: Formatted and wrapped text, or None if no content
    """
    print("\nEnter your notes (type '-done-' on its own line when finished)")
    print("=" * 50)
    
    lines = []
    while True:
        try:
            line = input()
            # Check for exit command
            if line.strip() == "-done-":
                break
            lines.append(line)
        except EOFError:
            break
    
    if not lines:
        return None
    
    # Join all lines and normalize tabs to 4 spaces
    text = "\n".join(lines).replace("\t", "    ")
    
    # Wrap text while preserving paragraph breaks (blank lines)
    paragraphs = text.split('\n')
    wrapped_lines = []
    
    for para in paragraphs:
        if para.strip():
            # Wrap non-empty paragraphs
            wrapped = textwrap.wrap(
                para,
                width=max_width,
                break_long_words=False,
                break_on_hyphens=False
            )
            wrapped_lines.extend(wrapped)
        else:
            # Preserve blank lines between paragraphs
            wrapped_lines.append("")
    
    return "\n".join(wrapped_lines)

def create_header(selected_dir, file_type):
    """
    Create a formatted header for the text file.
    
    Format:
        =====================================
        Game/Directory Name
        File Type (Control/Tips/Cheats)
        -------------------------------------
    
    Args:
        selected_dir: Name of the selected directory/game
        file_type: Type of file (control/tips/cheats)
        
    Returns:
        str: Formatted header text
    """
    header = "=" * 37 + "\n"
    header += selected_dir + "\n"
    #header += file_type.capitalize() + "\n"
    header += file_type.replace("_", " ").title() + "\n"
    header += "-" * 37 + "\n"
    return header

def upload_to_c64(local_file, remote_path):
    """
    Upload file to C64 Ultimate via FTP.
    
    Args:
        local_file: Path to local file to upload
        remote_path: Remote directory path on C64 Ultimate
        
    Returns:
        bool: True if upload successful, False otherwise
    """
    cmd = f'lftp -c "set net:timeout 5; open ftp://{TARGET_IP}; put -O \\"{remote_path}\\" \\"{local_file}\\""'
    
    try:
        subprocess.run(cmd, shell=True, check=True, timeout=10)
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False

def main():
    """
    Main program loop:
    1. Find C64 Ultimate on network
    2. Select target directory
    3. Create formatted text file (Control/Tips/Cheats)
    4. Upload to C64
    5. Repeat
    """
    global TARGET_IP
    
    # Initial IP discovery
    find_ultimate_ip()
    
    while True:
        # Select target directory on C64
        result = select_remote_dir()
        if not result:
            continue
        
        selected_dir, remote_path = result
        
        # Prompt for file type
        print("\nWhat type of file would you like to create?")
        print("1) Controls")
        print("2) Usage")
        print("3) Tips")
        print("4) Cheats")
        print("5) Full Manual")
        type_choice = input("Choice [1-5]: ").strip()
        
        # Map choice to file suffix
        suffix_map = {"1": "controls", "2": "usage", "3": "tips", "4": "cheats", "5": "full_manual"}
        suffix = suffix_map.get(type_choice, "notes")
        
        # Generate filename and temp file path
        new_name = f"{selected_dir}_{suffix}.txt"
        tmp_file = Path("/tmp") / new_name
        
        # Create content based on selected type
        if suffix == "controls":
            content = create_control_notes()
        else:
            content = create_freeform_notes()
        
        if content:
            # Write formatted file with header
            with open(tmp_file, 'w') as f:
                header = create_header(selected_dir, suffix)
                f.write(header + content + '\n')
            
            # Upload to C64
            if upload_to_c64(tmp_file, remote_path):
                print(f"\nSUCCESS: Pushed {new_name}")
            else:
                print("\nFAILED: Connection lost.")
                TARGET_IP = ""  # Clear cached IP to force rescan next time
        else:
            print("\nNo content entered. Skipping upload.")
        
        print("\nReturning to folder selection...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        exit(0)
