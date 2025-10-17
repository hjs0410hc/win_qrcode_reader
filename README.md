# QR Code Reader

A lightweight desktop application for capturing and decoding QR codes from your screen. Features a system tray icon for easy access and supports multi-monitor setups.

![App Icon](asset/icon.png)

![Platform](https://img.shields.io/badge/platform-Windows-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-GPLv3-green)

## Features

✨ **System Tray Integration** - Runs silently in the background with easy access from the system tray

🖱️ **Interactive Screen Capture** - Click and drag to select any region of your screen

🖥️ **Multi-Monitor Support** - Works seamlessly across all your displays, even with different DPI settings

🔍 **Instant QR Code Detection** - Automatically detects and decodes QR codes from the captured region

📋 **Quick Actions** - Copy decoded data to clipboard or open URLs directly from the result dialog

🔔 **Desktop Notification** - Windows toast lets you know when the tray app is ready

🎯 **DPI Aware** - Properly handles high-DPI displays and scaling

## Screenshots

### System Tray Icon

Right-click the icon to access the menu:

- Capture QR Code
- Quit

### Capture Mode

A semi-transparent overlay appears across all monitors. Simply drag to select the region containing a QR code.

### Result Dialog

When a QR code is detected, you'll see:

- The QR code type (QR_CODE, etc.)
- The decoded data
- Action buttons: Copy Data, Open URL (if applicable), Close

## Installation

### Option 1: Run from Source

1. **Clone the repository**

   ```bash
   git clone https://github.com/hjs0410hc/win_qrcode_reader.git
   cd win_qrcode_reader
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python qrcode_reader.py
   ```

### Option 2: Use Pre-built Executable (Windows)

1. Download the latest release from the [Releases](https://github.com/hjs0410hc/win_qrcode_reader/releases) page
2. Extract the ZIP file
3. Run `WinQRCodeReader.exe`

No installation or Python required!

## Building Executable

To build your own executable:

```bash
# Install PyInstaller
pip install pyinstaller

# Build the executable
pyinstaller qrcode_reader.spec
```

The executable will be created in the `dist` folder.

## Usage

1. **Start the application**

   - Run `python qrcode_reader.py` or double-click `WinQRCodeReader.exe`
   - The app will start minimized to the system tray

2. **Capture a QR code**

   - Right-click the tray icon (looks like a small QR code pattern)
   - Select "Capture QR Code"
   - A semi-transparent overlay appears across all your screens
   - Click and drag to select the region containing the QR code
   - Release to capture

3. **View results**

   - If a QR code is detected, a dialog shows the decoded data
   - Use the action buttons:
     - **Copy Data** - Copies the decoded text to your clipboard
     - **Open URL** - Opens the URL in your default browser (if the QR code contains a URL)
     - **Close** - Closes the result dialog

4. **Cancel capture**

   - Press `ESC` during capture mode to cancel

5. **Exit the application**
   - Right-click the tray icon and select "Quit"

## Requirements

- Python 3.8 or higher
- Windows 8.1+
- Multiple monitors supported
- Works with different DPI scaling settings

## Dependencies

- **Pillow** - Image processing
- **opencv-python** - Computer vision and image manipulation
- **pyzbar** - QR code decoding
- **pystray** - System tray icon functionality
- **mss** - Fast, cross-platform screen capture
- **winotify** - Windows toast notifications for readiness alerts
- **pyinstaller** - For building standalone executables

## Platform-Specific Notes

### Windows

- The tray icon appears in the system tray (bottom-right corner)
- DPI awareness is automatically enabled for accurate captures
- Works with Windows 8.1, 10, and 11

## Troubleshooting

**Tray icon doesn't appear**

- Check the hidden icons in the system tray (Windows)
- Verify the application is running in Task Manager/Activity Monitor

**No QR code detected**

- Ensure the QR code is fully visible in the selected region
- Try capturing a larger area around the QR code
- Make sure the QR code has good contrast and isn't blurry
- Check that the saved image file shows the correct region

**Black screen on secondary monitor**

- This should be fixed with the mss library
- Make sure you're running the latest version

## Development

### Project Structure

```
win_qrcode_reader/
├── qrcode_reader.py          # Main application
├── qrcode_reader.spec         # PyInstaller build configuration
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── LICENSE.md                 # License file
├── .gitignore                # Git ignore rules
├── asset                     # asset files
    └── icon.png              # Image file for tray icon
├── build/                     # Build artifacts (generated)
└── dist/                      # Distribution files (generated)
    └── WinQRCodeReader.exe       # Compiled executable
```

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the GPLv3 License - see the [LICENSE](LICENSE.md) file for details.

## Acknowledgments

- [pyzbar](https://github.com/NaturalHistoryMuseum/pyzbar) - QR code decoding
- [OpenCV](https://opencv.org/) - Computer vision library
- [pystray](https://github.com/moses-palmer/pystray) - System tray integration
- [mss](https://github.com/BoboTiG/python-mss) - Fast screen capture

## Author

Created with ❤️ by hjs0410hc

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/hjs0410hc/win_qrcode_reader/issues) on GitHub.

---

**Star ⭐ this repo if you find it useful!**
