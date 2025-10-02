# Test Scripts

## Available Tests

### 1. Keyboard Visual Test
**File:** `test_keyboard_visual.py`

Opens the lighting window to visually inspect the keyboard layout.

```bash
python3 test-scripts/test_keyboard_visual.py
```

**What to check:**
- Full 104-key layout visible
- Black background with colored borders
- 4 distinct zones with different colors
- Proper key sizes (Enter, Shift, Spacebar, etc.)
- Clean, professional appearance matching PredatorSense

### 2. Zone Colors Test
**File:** `test_zone_colors.py`

Tests reading and setting zone colors from the system.

```bash
python3 test-scripts/test_zone_colors.py
```

**Output:**
- Current zone colors (hex format)
- Current brightness level
- Success/failure of color setting

## Expected Keyboard Layout

### Zone Distribution:
```
┌─────────────────────────────────────────────────────────────────────────┐
│ [Zone 0: Left]  [Zone 1: Center-L]  [Zone 2: Center-R]  [Zone 3: Right]│
│                                                                          │
│ Esc F1-F4       F5-F8               F9-F12              PrtSc ScrLk Paus│
│                                                                          │
│ ` 1-5           6-7                 8-0 - = Bksp       Ins Home PgUp   │
│ Tab Q-T         Y-U                 I-P [ ] \          Del End  PgDn   │
│ Caps A-G        H-J                 K-; ' Enter                         │
│ Shift Z-V       B-N                 M-/ Shift              ↑           │
│ Ctrl Fn Win Alt Spacebar            AltGr Menu Ctrl     ← ↓ →         │
│                                                                          │
│                                                         [Numpad Zone 3] │
└─────────────────────────────────────────────────────────────────────────┘
```

### Key Features:
- **Zone 0 (Left)**: Yellow/Olive border - Left side keys
- **Zone 1 (Center-Left)**: Purple/Magenta border - Center-left + Spacebar
- **Zone 2 (Center-Right)**: Cyan/Blue border - Center-right keys
- **Zone 3 (Right)**: Green border - Navigation, arrows, numpad

## Troubleshooting

### Colors not reading correctly
Check if the system file exists:
```bash
cat /sys/module/linuwu_sense/drivers/platform:acer-wmi/acer-wmi/four_zoned_kb/per_zone_mode
```

Expected format: `color1,color2,color3,color4,brightness`

### Keyboard not displaying
Ensure PyQt5 is installed:
```bash
pip install PyQt5
```

### Permission issues
Some operations may require sudo. The app will prompt when needed.
