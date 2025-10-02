# RGB Keyboard Lighting Update

## Changes Made

### 1. Enhanced Lighting Service (`src/app/core/lighting_service.py`)
- Added `get_current_zone_colors()` method to read current zone colors from system
- Reads from `/sys/module/linuwu_sense/drivers/platform:acer-wmi/acer-wmi/four_zoned_kb/per_zone_mode`
- Returns tuple of (zone1_hex, zone2_hex, zone3_hex, zone4_hex, brightness)

### 2. Updated Keyboard Layout (`src/app/ui/lighting_window.py`)

#### Keyboard Visual Representation
- Updated to show realistic 4-zone keyboard layout
- 5 rows of keys matching actual keyboard structure
- Zone divisions:
  - **Zone 1 (Left)**: Columns 0-5 (Esc, F1-F5, ~, 1-5, Tab, Q-T, Caps, A-F, Shift, Z-C, Ctrl, Fn, Win, Alt)
  - **Zone 2 (Center-Left)**: Columns 6-10 (F6-F8, 6-8, Y-I, G-K, V-M)
  - **Zone 3 (Center-Right)**: Columns 11-15 (F9-F11, 9-0, O-P, L-;, ,-./)
  - **Zone 4 (Right)**: Columns 16+ (F12, Del, Backspace, Enter, Shift, numpad, etc.)
- Visual zone dividers with dashed lines
- Keys colored according to their zone

#### Zone Controls
- Replaced preset cyan/purple buttons with full color pickers
- Each zone now has:
  - Descriptive label (Zone 1-4 with position name)
  - Color picker button showing current color
  - Immediate color application on change
- Zone names:
  - Zone 1: Left
  - Zone 2: Center-Left
  - Zone 3: Center-Right
  - Zone 4: Right

#### Initialization
- Reads current zone colors from system on startup
- Displays actual current colors instead of defaults
- Falls back to cyan/purple defaults if read fails

### 3. Test Script
- Created `test-scripts/test_zone_colors.py` to verify functionality
- Tests reading current colors from system
- Validates color setting functionality

## How It Works

1. **On Startup**: The lighting window reads current zone colors from the system file
2. **Visual Display**: The keyboard widget shows all keys colored by their zone
3. **Color Selection**: Click any zone's color button to open a color picker
4. **Immediate Application**: Changes are applied to the keyboard immediately
5. **Brightness Control**: Slider at top adjusts overall brightness

## System Integration

The application reads from:
```
/sys/module/linuwu_sense/drivers/platform:acer-wmi/acer-wmi/four_zoned_kb/per_zone_mode
```

Format: `color1,color2,color3,color4,brightness`
Example: `810cf5,810cf5,810cf5,810cf5,100`

## Testing

Run the test script to verify:
```bash
python3 test-scripts/test_zone_colors.py
```

Or launch the full application:
```bash
python3 src/main.py
```

Then navigate to the Lighting tab and select "Static" mode.
