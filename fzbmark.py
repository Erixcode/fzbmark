#!/usr/bin/env python3
import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any
import argparse
import glob

class BrowserBookmarkManager:
    def __init__(self):
        self.browser_profiles = self.detect_browser_profiles()
    
    def detect_browser_profiles(self) -> Dict[str, List[str]]:
        """Find browser bookmark files"""
        profiles = {}
        
        # Firefox
        firefox_path = Path.home() / '.mozilla' / 'firefox'
        if firefox_path.exists():
            profiles['firefox'] = [
                str(p) for p in firefox_path.glob('*/places.sqlite') 
                if p.stat().st_size > 0
            ]
        
        # Chrome/Chromium/Brave
        chromium_browsers = {
            'chrome': '~/.config/google-chrome',
            'chromium': '~/.config/chromium', 
            'brave': '~/.config/BraveSoftware/Brave-Browser'
        }
        
        for browser, path in chromium_browsers.items():
            config_path = Path(path).expanduser()
            if config_path.exists():
                bookmark_files = list(config_path.glob('*/Bookmarks'))
                if bookmark_files:
                    profiles[browser] = [str(p) for p in bookmark_files]
        
        return profiles
    
    def parse_firefox_bookmarks(self, db_path: str) -> List[Dict[str, str]]:
        """Parse Firefox SQLite bookmarks"""
        bookmarks = []
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.execute("""
                SELECT moz_places.url, moz_bookmarks.title 
                FROM moz_places 
                JOIN moz_bookmarks ON moz_places.id = moz_bookmarks.fk
                WHERE moz_bookmarks.type = 1 AND moz_places.url IS NOT NULL
            """)
            
            for url, title in cursor:
                if url.startswith(('http://', 'https://')):
                    bookmarks.append({
                        'url': url,
                        'title': title or url,
                        'source': 'firefox'
                    })
        except sqlite3.Error as e:
            print(f"Error reading Firefox bookmarks: {e}")
        
        return bookmarks
    
    def parse_chromium_bookmarks(self, json_path: str, browser: str) -> List[Dict[str, str]]:
        """Parse Chrome/Chromium/Brave JSON bookmarks"""
        bookmarks = []
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Recursively extract bookmarks from folders
            def extract_from_node(node: Dict[str, Any]) -> None:
                if 'children' in node:
                    for child in node['children']:
                        extract_from_node(child)
                elif node.get('type') == 'url' and 'url' in node:
                    bookmarks.append({
                        'url': node['url'],
                        'title': node.get('name', node['url']),
                        'source': browser
                    })
            
            if 'roots' in data:
                for root in data['roots'].values():
                    if isinstance(root, dict):
                        extract_from_node(root)
                        
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error reading {browser} bookmarks: {e}")
        
        return bookmarks
    
    def get_all_bookmarks(self) -> List[Dict[str, str]]:
        """Get all bookmarks from all detected browsers"""
        all_bookmarks = []
        
        for browser, paths in self.browser_profiles.items():
            for path in paths:
                if browser == 'firefox':
                    all_bookmarks.extend(self.parse_firefox_bookmarks(path))
                else:
                    all_bookmarks.extend(self.parse_chromium_bookmarks(path, browser))
        
        return all_bookmarks
    
    def open_url(self, url: str, browser: str = None):
        """Open URL in appropriate browser"""
        if browser:
            # Open in specific browser if requested
            subprocess.Popen([browser, url])
        else:
            # Use default browser
            subprocess.Popen(['xdg-open', url])

def main():
    parser = argparse.ArgumentParser(description="Terminal Browser Bookmark Manager")
    parser.add_argument("--browser", choices=['firefox', 'chrome', 'brave', 'chromium'], 
                       help="Use specific browser's bookmarks")
    parser.add_argument("--list-browsers", action='store_true', 
                       help="List detected browsers with bookmarks")
    parser.add_argument("--list", action='store_true', 
                       help="List all bookmarks without opening")
    parser.add_argument("--search", help="Search term (shows matching bookmarks)")
    
    args = parser.parse_args()
    manager = BrowserBookmarkManager()
    
    if args.list_browsers:
        print("Detected browsers with bookmarks:")
        for browser, paths in manager.browser_profiles.items():
            print(f"  {browser}: {len(paths)} profile(s)")
        return
    
    bookmarks = manager.get_all_bookmarks()
    
    if not bookmarks:
        print("No bookmarks found in any browser!")
        print("Supported browsers: Firefox, Chrome, Chromium, Brave")
        return
    
    if args.list:
        for i, bm in enumerate(bookmarks, 1):
            print(f"{i:3d}. {bm['title'][:50]:50} | {bm['url'][:50]:50} | {bm['source']}")
        return
    
    if args.search:
        # Filter bookmarks by search term
        search_lower = args.search.lower()
        filtered = [
            bm for bm in bookmarks 
            if search_lower in bm['title'].lower() or search_lower in bm['url'].lower()
        ]
        
        if not filtered:
            print(f"No bookmarks found matching '{args.search}'")
            return
            
        for i, bm in enumerate(filtered, 1):
            print(f"{i:3d}. {bm['title']}")
        
        try:
            choice = input("\nSelect bookmark number (or Enter to cancel): ").strip()
            if choice and choice.isdigit():
                selected = filtered[int(choice) - 1]
                manager.open_url(selected['url'], selected['source'] if selected['source'] != 'firefox' else 'firefox')
        except (ValueError, IndexError):
            print("Invalid selection")
        return
    
    # Interactive mode with fzf
    try:
        # Prepare input for fzf (title | url | source)
        fzf_input = "\n".join(
            f"{bm['title']} | {bm['url']} | {bm['source']}" 
            for bm in bookmarks
        )
        
        # Run fzf with custom preview
        result = subprocess.run([
            'fzf', 
            '--delimiter', '|', 
            '--with-nth', '1,3',  # Show title and source
            '--preview', 'echo {2} | cut -c1-80',  # Show URL preview
            '--preview-window', 'down:1:wrap'
        ], input=fzf_input, text=True, capture_output=True)
        
        if result.returncode == 0 and result.stdout.strip():
            selected_line = result.stdout.strip()
            selected_url = selected_line.split('|')[1].strip()
            selected_source = selected_line.split('|')[2].strip()
            
            # Determine which browser to use
            browser_cmd = None
            if selected_source == 'firefox':
                browser_cmd = 'firefox'
            elif selected_source in ['chrome', 'chromium', 'brave']:
                browser_cmd = selected_source
            
            manager.open_url(selected_url, browser_cmd)
            
    except FileNotFoundError:
        print("Error: fzf not found. Please install fzf to use interactive mode.")
        print("You can use --search or --list options instead.")

if __name__ == "__main__":
    main()
