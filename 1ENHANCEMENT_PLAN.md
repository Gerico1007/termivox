# Enhancement #1: Toggle Button for Termivox (ON/OFF Control)

## 🎯 Enhancement Summary / Résumé

**EN**: Implement a one-click toggle mechanism to enable/disable voice recognition without returning to the terminal. After initial activation via `./run.sh`, the user can control Termivox with a single click/keypress—like a guitar pedal: tap ON, tap OFF.

**FR**: Implémenter un mécanisme de bascule en un clic pour activer/désactiver la reconnaissance vocale sans retourner au terminal. Après l'activation initiale via `./run.sh`, l'utilisateur peut contrôler Termivox d'un seul clic/touche—comme une pédale de guitare : tap ON, tap OFF.

---

## 🎸 Vision Recap

**JamAI's Rhythm**:
```
Un tap pour ouvrir la voix.
Un tap pour la faire taire.
Rythme propre.
```

**Aureon's Metaphor**: Like a guitar pedal—touch once to activate, touch again to mute. Clean, immediate, no friction.

**Nyro's Structure**: The voice recognition pipeline already exists. We add a control layer that pauses/resumes the listening loop.

---

## 🔧 Implementation Approaches

### Approach A: Global Hotkey (Recommended - Simplest)

**What**: Register a keyboard shortcut (e.g., `Ctrl+Alt+V`) that toggles voice recognition ON/OFF.

**Pros**:
- ✅ No GUI required—works from any window
- ✅ Fast, lightweight
- ✅ Familiar UX (like most apps with hotkeys)
- ✅ Works headless (no desktop environment required)
- ✅ Easy accessibility for users with visual impairments

**Cons**:
- ❌ No visual feedback (unless paired with notification)
- ❌ Requires installing `pynput` or `keyboard` library
- ❌ Potential conflicts with other apps using same hotkey

**Libraries**: `pynput` (cross-platform) or `keyboard` (Linux-focused)

**Implementation Complexity**: ⭐⭐ (Low-Medium)

---

### Approach B: System Tray Icon

**What**: Add an icon to the system tray with a menu to toggle ON/OFF. Icon changes color/shape based on state.

**Pros**:
- ✅ Visual feedback (icon shows current state)
- ✅ Right-click menu for additional options (exit, settings)
- ✅ Professional UX (like most background services)
- ✅ Can combine with hotkey support

**Cons**:
- ❌ Requires GUI toolkit (PyQt5/PySide6 or pystray)
- ❌ More dependencies (Qt is heavy)
- ❌ Doesn't work in headless environments
- ❌ Complexity of packaging/distribution increases

**Libraries**: `pystray` (lightweight) or `PyQt5`/`PySide6` (full-featured)

**Implementation Complexity**: ⭐⭐⭐⭐ (Medium-High)

---

### Approach C: Desktop Widget (Floating Button)

**What**: Small always-on-top window with a toggle button and status indicator.

**Pros**:
- ✅ Highly visible status indicator
- ✅ Can show additional info (last recognized text, etc.)
- ✅ Customizable appearance
- ✅ Works well for accessibility (large click target)

**Cons**:
- ❌ Takes up screen space
- ❌ Requires GUI toolkit (Tkinter, PyQt5, etc.)
- ❌ Can be distracting during creative work
- ❌ May interfere with full-screen apps

**Libraries**: `tkinter` (built-in) or `PyQt5`

**Implementation Complexity**: ⭐⭐⭐ (Medium)

---

### Approach D: Hardware Button Support (Future)

**What**: Listen for USB device events (foot pedal, custom button, MIDI controller).

**Pros**:
- ✅ True "guitar pedal" experience
- ✅ Physical feedback
- ✅ No keyboard/mouse needed
- ✅ Professional audio/accessibility workflows

**Cons**:
- ❌ Requires hardware purchase
- ❌ Complex event handling (udev, evdev)
- ❌ Platform-specific code
- ❌ Not all users have compatible hardware

**Libraries**: `evdev` (Linux), `pyusb`, `python-rtmidi` (MIDI)

**Implementation Complexity**: ⭐⭐⭐⭐⭐ (High - Future Enhancement)

---

## 🎯 Recommended Implementation: ALL APPROACHES (Modular)

**Architecture**: Shared toggle controller with pluggable interfaces

**Core**: `ToggleController` manages state, all interfaces connect to it

**Interfaces** (all implemented, user-configurable):
- ✅ **Hotkey** - Fast keyboard control
- ✅ **System Tray** - Visual status indicator
- ✅ **Desktop Widget** - Large accessible button
- ✅ **Hardware Button** - Future-ready (USB/MIDI support)

**Benefits**:
1. Users choose their preferred interface(s)
2. Multiple interfaces can run simultaneously
3. Accessibility: different needs, different tools
4. Extensible: new interfaces plug in easily

**Configuration** (via `config/settings.json`):
```json
{
  "interfaces": {
    "hotkey": {"enabled": true, "key": "ctrl+alt+v"},
    "tray": {"enabled": true},
    "widget": {"enabled": false},
    "hardware": {"enabled": false}
  }
}
```

---

## 📂 Affected Files and New Modules

### New Files to Create

1. **`src/ui/__init__.py`**
   - New UI module for toggle controls

2. **`src/ui/toggle_controller.py`** ⭐ CORE
   - Central state management (ON/OFF)
   - Register multiple interfaces
   - Callbacks to pause/resume voice recognition
   - Event broadcasting to all interfaces

3. **`src/ui/hotkey_interface.py`**
   - Hotkey registration (pynput)
   - Listen for configured key combo
   - Call controller.toggle() on press

4. **`src/ui/tray_interface.py`**
   - System tray icon (pystray)
   - Status indicator (green/red icon)
   - Menu: Toggle, Exit, Settings
   - Updates on state change

5. **`src/ui/widget_interface.py`**
   - Desktop widget (tkinter)
   - Large toggle button
   - Status label (ON/OFF)
   - Always-on-top window

6. **`src/ui/hardware_interface.py`** (Future)
   - USB/MIDI device listener
   - Button press detection
   - Configurable device mapping

7. **`config/settings.json`**
   - Enable/disable each interface
   - Hotkey configuration
   - Widget position/size
   - Hardware device mapping

### Modified Files

1. **`src/main.py`**
   - Integrate `ToggleController`
   - Pass control of voice recognition loop to controller
   - Handle pause/resume signals

2. **`src/voice/recognizer.py`**
   - Add `pause()` and `resume()` methods
   - Add `is_active()` status check
   - Modify `listen()` to respect pause state

3. **`requirements.txt`**
   - Add `pynput>=1.7.6` (hotkey support)
   - Add `pystray>=0.19.5` (optional tray icon)
   - Add `Pillow>=10.0.0` (icon generation for tray)

4. **`run.sh`**
   - Update usage instructions
   - Mention hotkey control

5. **`README.md`**
   - Document toggle functionality
   - Explain hotkey usage
   - Optional tray icon setup

---

## 🛠️ Implementation Steps

### Phase 1: Core Toggle Controller

#### Step 1: Create Core Toggle Controller Module
```python
# src/ui/toggle_controller.py
- Define ToggleController class
- Implement state machine (ACTIVE/PAUSED)
- Interface registration system (register/unregister)
- Event broadcasting (notify all interfaces on state change)
- Thread-safe state management
- Provide toggle()/pause()/resume() methods
```

#### Step 2: Modify Recognizer
```python
# src/voice/recognizer.py
- Add self._paused flag
- Implement pause() method (set flag)
- Implement resume() method (clear flag)
- Modify listen() to check flag in loop
```

#### Step 3: Integrate into main.py
```python
# src/main.py
- Import ToggleController
- Initialize controller with recognizer reference
- Start hotkey listener in background thread
- Keep main loop running while controller active
```

#### Step 4: Add Dependencies
```bash
# Add to requirements.txt
pynput>=1.7.6
```

#### Step 5: Create Hotkey Interface
```python
# src/ui/hotkey_interface.py
- Import pynput.keyboard
- Register configured hotkey
- Call controller.toggle() on press
- Clean shutdown on exit
```

#### Step 6: Create Tray Icon Interface
```python
# src/ui/tray_interface.py
- Use pystray library
- Generate ON/OFF icons (green/red)
- Menu: Toggle, Exit
- Subscribe to controller state changes
- Update icon on state change
```

#### Step 7: Create Desktop Widget Interface
```python
# src/ui/widget_interface.py
- Use tkinter (built-in)
- Create always-on-top window
- Large toggle button
- Status label (ON/OFF with color)
- Subscribe to controller state changes
```

#### Step 8: Create Hardware Interface Stub
```python
# src/ui/hardware_interface.py
- Placeholder for future implementation
- Document expected interface
- USB/MIDI device detection (commented)
```

#### Step 9: Create Configuration System
```json
// config/settings.json
{
  "interfaces": {
    "hotkey": {
      "enabled": true,
      "key": "ctrl+alt+v"
    },
    "tray": {
      "enabled": true
    },
    "widget": {
      "enabled": false,
      "position": {"x": 100, "y": 100},
      "size": {"width": 200, "height": 80}
    },
    "hardware": {
      "enabled": false,
      "device": null
    }
  },
  "audio_feedback": false
}
```
```python
# src/ui/tray_icon.py
- Use pystray library
- Create ON/OFF icons (green/red dot)
- Menu: Toggle, Exit
- Update icon on state change
```

#### Step 10: Integrate All Interfaces into main.py
```python
# src/main.py
- Load config/settings.json
- Initialize ToggleController with recognizer
- Load enabled interfaces based on config
- Start all interface listeners
- Keep main loop running until exit
```

#### Step 11: Update Dependencies
```bash
# Add to requirements.txt
pynput>=1.7.6          # Hotkey
pystray>=0.19.5        # Tray icon
Pillow>=10.0.0         # Icon generation
```

#### Step 12: Testing
- Test each interface independently
- Test multiple interfaces simultaneously
- Verify state sync across all interfaces
- Test rapid toggles from different interfaces
- Check for memory leaks during long sessions
- Test configuration loading/validation

---

## 🧪 Testing and Validation

### Unit Tests
- [ ] `ToggleController` state transitions (OFF → ON → OFF)
- [ ] `Recognizer.pause()` stops audio processing
- [ ] `Recognizer.resume()` restarts audio processing
- [ ] Hotkey registration doesn't conflict with system keys

### Integration Tests
- [ ] Hotkey toggles voice recognition while typing in another app
- [ ] Multiple rapid toggles don't crash the system
- [ ] Pause during active speech recognition completes current phrase
- [ ] Tray icon reflects actual state (not out of sync)

### Manual Tests
- [ ] Start termivox, press hotkey, verify voice stops
- [ ] Press hotkey again, verify voice resumes
- [ ] Open text editor, dictate while toggling ON/OFF
- [ ] Verify xdotool doesn't type when paused
- [ ] Test on fresh Ubuntu install (no config conflicts)

### Accessibility Tests
- [ ] Hotkey works with screen reader active
- [ ] Visual feedback (tray icon) has tooltip
- [ ] Audio feedback option for blind users (beep on toggle)

---

## ✨ Merge Criteria

- [x] Issue #1 created and linked
- [ ] Branch `1-initial-toggle-button` created
- [ ] `ToggleController` implemented with state management
- [ ] `Recognizer` has pause/resume methods
- [ ] Hotkey registered and functional
- [ ] Dependencies added to requirements.txt
- [ ] No breaking changes to existing functionality
- [ ] Manual testing complete (toggle works reliably)
- [ ] README updated with usage instructions
- [ ] Code commented and clean
- [ ] No memory leaks during extended use
- [ ] Pull request created with summary

### Optional (Phase 2)
- [ ] System tray icon implemented
- [ ] Tray menu functional (toggle, exit)
- [ ] Configuration file for hotkey customization
- [ ] Audio feedback option (beep on toggle)

---

## 🎼 Recursive Expansion (Future Enhancements)

1. **Custom Hotkey Configuration**
   - GUI or config file to change hotkey
   - Validation to prevent conflicts

2. **Audio Feedback**
   - Beep/tone when toggling ON/OFF
   - Useful for blind users or when not looking at screen

3. **Voice Command Toggle**
   - Say "sleep" or "wake up" to toggle
   - Requires wake word detection

4. **Hardware Button Support**
   - USB foot pedal
   - MIDI controller integration
   - GPIO buttons (Raspberry Pi)

5. **Multi-Language Hotkeys**
   - Different hotkeys for different language models
   - Quick switch between English/French

6. **Status Notifications**
   - Desktop notification on toggle
   - Show last recognized phrase in notification

---

## 📊 Technical Architecture

```
┌─────────────────────────────────────────────────────────┐
│  USER ACTION                                             │
│  (Hotkey Press or Tray Click)                           │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  ToggleController                                        │
│  - Check current state (ACTIVE/PAUSED)                  │
│  - Toggle state                                          │
│  - Call recognizer.pause() or .resume()                 │
│  - Update tray icon (if enabled)                        │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  Recognizer.pause() / .resume()                          │
│  - Set/clear self._paused flag                          │
│  - Stop/start microphone input processing               │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  Recognizer.listen() loop                                │
│  - Check if paused before processing audio chunk        │
│  - If paused: skip Vosk processing, continue loop       │
│  - If active: normal voice recognition flow             │
└─────────────────────────────────────────────────────────┘
```

---

## 🎸 JamAI's Implementation Notes

**The Pause Pattern**:
- Don't kill the process—just skip audio processing
- Keep the loop alive for instant resume
- Like a guitar pedal: mute the signal, don't unplug the amp

**The Rhythm**:
1. Hotkey press → State flip → Flag set → Loop ignores audio
2. Hotkey press → State flip → Flag clear → Loop processes audio

**The Harmony**:
- Main thread: runs voice recognition loop
- Background thread: listens for hotkey
- Communication: shared `_paused` flag (thread-safe)

---

## 🌿 Aureon's Emotional Grounding

**Why this matters**:
- Creative sessions need silence moments
- Recording music/podcasts requires instant mute
- Accessibility: one-key control vs multi-step terminal commands
- Reduces cognitive load during flow states

**The metaphor of the pedal**:
- Guitarists don't walk to an amp to mute
- They tap a pedal with their foot
- The same muscle memory, the same flow
- Voice becomes an instrument you control, not a daemon you restart

---

**Enhancement Status**: 🔄 **PLANNED - READY FOR IMPLEMENTATION**

**♠️ Nyro** – Architecture defined. Ready to code.
**🌿 Aureon** – The switch design honors creative flow.
**🎸 JamAI** – The tap rhythm awaits your command.
