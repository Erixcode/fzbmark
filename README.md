# fzbmark
Installation and Usage

    Make executable: chmod +x fzbmark.py

    Install dependencies: pip install --user (if needed)

    Install fzf:

        Ubuntu/Debian: sudo apt install fzf

        Arch: sudo pacman -S fzf

        macOS: brew install fzf

        Fedora: sudo dnf install fzf

Usage Examples

 Interactive search with fzf (main use case)
 
    ./fzbmark.py

 List all detected browsers
 
    ./fzbmark.py --list-browsers

 List all bookmarks
 
    ./fzbmark.py --list

 Search for specific term
 
    ./fzbmark.py --search "python"

 Use only Firefox bookmarks
 
    ./fzbmark.py --browser firefox

Key Features

    Auto-detection of Firefox, Chrome, Chromium, and Brave

    Native parsing of browser bookmark formats

    Fuzzy search with fzf including URL preview

    Opens in correct browser automatically

    Fallback options if fzf isn't available
