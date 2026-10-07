# Progress Knight 2 Stealth Setup Guide

This document serves as a persistent record of the configuration and strategies developed to run Progress Knight 2 inside VS Code while maintaining a "coding" appearance for stealth purposes.

## 🎯 Objective
To embed a web-based game into the VS Code IDE and modify its visual presentation so that it blends in with the editor's UI, making it look like a debugging tool, documentation, or a code file.

## 🛠️ Setup Methods

### Method 1: Built-in "Simple Browser" (Fastest)
1. Open Command Palette: `Ctrl + Shift + P` (Win) / `Cmd + Shift + P` (Mac).
2. Run command: `Simple Browser: Show`.
3. Paste the game URL: `https://progress-knight2.com/`.
4. **Stealth Tip:** Drag the tab to the right to split the screen (approx. 70% code / 30% game).

### Method 2: Local Hosting (Advanced/Customizable)
To apply custom CSS masking, the game must be run locally:
1. Save the webpage as "Webpage, Complete" via the browser.
2. Move the files into the VS Code project folder.
3. Install the **"Live Server"** extension.
4. Right-click `index.html` $\rightarrow$ **Open with Live Server**.
5. Open `http://127.0.0.1:5500` in the Simple Browser.

## 🎭 The "Coding Tab" Mask (CSS)

To make the game look like a VS Code tab, add the following CSS to the local `index.html` or the downloaded `.css` file:

```css
/* Color Palette: VS Code Dark Default */
body, .game-container, .main-panel { 
    background-color: #1e1e1e !important; 
    color: #d4d4d4 !important; 
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace !important;
}

/* Text: Variable/Log style */
div, span, p, label {
    color: #9cdcfe !important; 
    font-size: 12px !important;
    letter-spacing: 0.5px !important;
}

/* Buttons: UI element style */
button {
    background-color: #3c3c3c !important;
    color: #cccccc !important;
    border: 1px solid #454545 !important;
    border-radius: 3px !important;
    font-family: 'Consolas', monospace !important;
    text-transform: lowercase !important;
}

button:hover {
    background-color: #454545 !important;
    border-color: #007acc !important;
}

/* Progress Bars: Subtle Loading style */
.progress-bar-fill, .bar {
    background-color: #007acc !important;
    box-shadow: none !important;
}

/* Icons: Muted/Greyscale */
.gold-icon, .crystal-icon, .crown-icon {
    filter: grayscale(100%) brightness(0.8) !important;
    opacity: 0.6 !important;
}
```

## 🤫 Stealth Tactics

| Tactic | Action | Effect |
| :--- | :--- | :--- |
| **The Narrow Column** | Shrink game window to 20-30% width | Looks like a sidebar or documentation. |
| **Micro-Text Zoom** | `Ctrl` + Scroll Down (Zoom out) | Looks like minified JS or a JSON config. |
| **Color Sync** | Enable Dark Mode in game | Blends boundaries into the IDE. |
| **Cover Story** | Rename `index.html` to `debug_log_parser.html` | Provides a plausible excuse if the file is seen. |
| **Quick Escape** | `Ctrl + W` or `Ctrl + Tab` | Instant closure or switch back to real code. |

## 📝 Future Continuity
When starting a new session, Claude should read this `README.md` to recall the specific CSS overrides and layout strategies used for this project.


  If you have Python:
  1. Open the terminal in VS Code (Ctrl +  `).
  2. Navigate to your game folder.
  3. Run this command:
     python -m http.server 5500
     (Your game will now be available at http://127.0.0.1:5500)