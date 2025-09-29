# Function to set WM_CLASS for the window
def set_wm_class(win_id, instance_name, class_name):
    """Attempt to set WM_CLASS on X11. No-op on systems without Xlib/X11."""
    try:
        from Xlib import display
        from Xlib.Xatom import STRING
    except Exception as e:
        # Xlib not available; likely Wayland or dependency missing
        print(f"Xlib unavailable, skipping WM_CLASS: {e}")
        return

    try:
        disp = display.Display()
        window = disp.create_resource_object('window', win_id)
        wm_class_atom = disp.intern_atom('WM_CLASS')
        value = f'{instance_name}\0{class_name}\0'.encode('utf-8')
        window.change_property(wm_class_atom, STRING, 8, value)
        disp.flush()
    except Exception as e:
        print(f"Failed to set WM_CLASS on X11: {e}")