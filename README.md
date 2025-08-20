# fzbmark
Installation and Usage:

Install dependencies: <code>pip install --user</code> (if needed)<br>
Install fzf:

        Ubuntu/Debian: sudo apt install fzf
        Arch: sudo pacman -S fzf
        macOS: brew install fzf
        Fedora: sudo dnf install fzf
        Gentoo: sudo emerge --ask app-shells/fzf
    
Make executable: <code>chmod +x fzbmark.py</code>

Usage Examples:
 Interactive search with fzf (main use case):
 
    ./fzbmark.py

 List all detected browsers:
 
    ./fzbmark.py --list-browsers

 List all bookmarks:
 
    ./fzbmark.py --list

 Search for specific term:
 
    ./fzbmark.py --search "python"

 Use only Firefox bookmarks:
 
    ./fzbmark.py --browser firefox

Key Features:

  --  Auto-detection of Firefox, Chrome, Chromium, and Brave<br>
  --  Native parsing of browser bookmark formats<br>
  --  Fuzzy search with fzf including URL preview<br>
  --  Opens in correct browser automatically<br>
  --  Fallback options if fzf isn't available<br>
