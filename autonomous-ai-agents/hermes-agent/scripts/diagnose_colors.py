#!/usr/bin/env python3
"""
Hermes Color Configuration Diagnostics

Quickly check Hermes skin/personality settings and color codes.
Run this to diagnose why Hermes output appears yellow/wrong color.
"""

import os
import sys
import yaml
from pathlib import Path

def print_section(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)

def load_config():
    """Load Hermes config.yaml"""
    config_path = Path.home() / '.hermes' / 'config.yaml'
    if not config_path.exists():
        print(f"✗ Config not found: {config_path}")
        return None
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def get_skin_colors(skin_name):
    """Load color definitions from skin file"""
    skin_path = Path.home() / '.hermes' / 'skins' / f'{skin_name}.yaml'
    if not skin_path.exists():
        return None
    
    with open(skin_path, 'r') as f:
        skin_data = yaml.safe_load(f)
    
    return skin_data.get('colors', {})

def main():
    print_section("Hermes Color Configuration Diagnostics")
    
    # Load config
    config = load_config()
    if not config:
        print("✗ Cannot load config - exiting")
        sys.exit(1)
    
    # Check agent settings
    agent_config = config.get('agent', {})
    
    print("\n[Current Settings]")
    print(f"  Skin:        {agent_config.get('skin', 'not set')}")
    print(f"  Personality: {agent_config.get('personality', 'not set')}")
    
    # Warn about kawaii personality
    personality = agent_config.get('personality')
    if personality == 'kawaii':
        print("\n⚠ WARNING: 'kawaii' personality uses gold/cornsilk colors")
        print("  This may appear yellow/cream even with dark skin.")
        print("  Fix: hermes config set agent.personality default")
    
    # Load and display skin colors
    skin_name = agent_config.get('skin')
    if skin_name:
        print_section(f"Skin Colors: {skin_name}")
        
        colors = get_skin_colors(skin_name)
        if colors:
            print("\nKey colors:")
            key_colors = [
                ('banner_text', 'Main banner text'),
                ('prompt', 'Prompt symbol'),
                ('response_border', 'Response border'),
                ('status_bar_text', 'Status bar text'),
                ('ui_error', 'Error messages'),
                ('ui_warn', 'Warning messages'),
                ('ui_ok', 'Success messages'),
            ]
            
            has_non_black = False
            for color_key, description in key_colors:
                color_code = colors.get(color_key, 'not set')
                status = "✓" if color_code == "#000000" else " "
                if color_key in ['banner_text', 'prompt', 'response_border'] and color_code != "#000000":
                    has_non_black = True
                print(f"  {status} {description:20s} = {color_code}")
            
            if has_non_black:
                print("\n⚠ WARNING: Some key colors are not #000000 (pure black)")
                print("  User requires pure black (#000000) on white backgrounds.")
        else:
            print(f"  ✗ Skin file not found: ~/.hermes/skins/{skin_name}.yaml")
    
    # List available skins
    print_section("Available Skins")
    skins_dir = Path.home() / '.hermes' / 'skins'
    if skins_dir.exists():
        skins = list(skins_dir.glob('*.yaml'))
        print(f"\nFound {len(skins)} skin(s):")
        for skin in skins:
            is_active = skin.stem == skin_name
            mark = "→" if is_active else " "
            print(f"  {mark} {skin.stem}")
    else:
        print("  ✗ Skins directory not found")
    
    # Color recommendations
    print_section("Recommendations")
    
    if personality == 'kawaii':
        print("\n1. Change personality from 'kawaii' to avoid yellow/cream colors:")
        print("   hermes config set agent.personality default")
    
    if skin_name != 'light-black':
        print("\n2. Consider using 'light-black' skin for pure black text:")
        print("   hermes config set agent.skin light-black")
    
    print("\n3. After changing settings, restart Hermes:")
    print("   - CLI: Exit and run 'hermes' again")
    print("   - Gateway: /restart")
    
    print("\n4. Verify changes:")
    print("   hermes config show | grep -A 5 'agent:'")
    
    print_section("User Color Preference")
    print("\nREQUIRED: Pure black (#000000) on white backgrounds")
    print("NEVER use: #222222, #333333, or gray variants for 'black' text")
    print("\nWhen setting colors for any UI element:")
    print("  ✓ CORRECT: color='#000000'")
    print("  ✗ WRONG:   color='#222222' or any gray")

if __name__ == '__main__':
    main()
