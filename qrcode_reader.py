"""
QR Code Reader with System Tray
Captures a screen region and detects/decodes QR codes
"""

import sys
import threading
import os
from PIL import Image
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import pystray
from pystray import MenuItem as item
import tkinter as tk
from tkinter import messagebox
import mss
import ctypes

# Make application DPI aware for Windows
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()  # Windows 8.1 and earlier
    except Exception:
        pass  # DPI awareness not available


def get_dpi_scale():
    """Get the DPI scaling factor for primary monitor"""
    try:
        # Get DPI scaling factor
        user32 = ctypes.windll.user32
        dpi = user32.GetDpiForSystem()
        scale = dpi / 96.0  # 96 is the default DPI
        return scale
    except Exception:
        return 1.0  # Default to no scaling


def get_all_monitors():
    """Get information about all monitors"""
    try:
        user32 = ctypes.windll.user32
        # Get virtual screen dimensions (covers all monitors)
        x = user32.GetSystemMetrics(76)  # SM_XVIRTUALSCREEN
        y = user32.GetSystemMetrics(77)  # SM_YVIRTUALSCREEN
        width = user32.GetSystemMetrics(78)  # SM_CXVIRTUALSCREEN
        height = user32.GetSystemMetrics(79)  # SM_CYVIRTUALSCREEN
        
        return {
            'x': x,
            'y': y,
            'width': width,
            'height': height
        }
    except Exception:
        # Fallback to primary monitor
        return {
            'x': 0,
            'y': 0,
            'width': user32.GetSystemMetrics(0),  # SM_CXSCREEN
            'height': user32.GetSystemMetrics(1)  # SM_CYSCREEN
        }


class ScreenCaptureOverlay:
    """Full-screen overlay for selecting a region to capture - spans all monitors"""
    
    def __init__(self, callback):
        self.callback = callback
        self.dpi_scale = get_dpi_scale()
        self.monitors = get_all_monitors()
        
        self.root = tk.Tk()
        
        # Position and size to cover all monitors
        geometry = f"{self.monitors['width']}x{self.monitors['height']}+{self.monitors['x']}+{self.monitors['y']}"
        self.root.geometry(geometry)
        self.root.overrideredirect(True)  # Remove window decorations
        self.root.attributes('-alpha', 0.3)
        self.root.attributes('-topmost', True)
        self.root.configure(bg='black')
        self.root.config(cursor="cross")
        
        self.canvas = tk.Canvas(self.root, cursor="cross", bg='black', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.start_x = None
        self.start_y = None
        self.rect = None
        
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.root.bind("<Escape>", lambda e: self.cancel())
        
        # Instructions (centered relative to virtual screen)
        label = tk.Label(
            self.root, 
            text=f"Drag to select area • ESC to cancel | All Monitors: {self.monitors['width']}x{self.monitors['height']}",
            bg='black',
            fg='white',
            font=('Arial', 14)
        )
        # Position at top center of virtual screen
        label.place(x=self.monitors['width']//2, y=30, anchor='center')
        
    def on_press(self, event):
        # Use root coordinates (screen coordinates) instead of window coordinates
        self.start_x = event.x_root
        self.start_y = event.y_root
        # But use regular coordinates for drawing on canvas
        self.start_canvas_x = event.x
        self.start_canvas_y = event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(
            self.start_canvas_x, self.start_canvas_y, 
            self.start_canvas_x, self.start_canvas_y,
            outline='red', width=3
        )
        
    def on_drag(self, event):
        if self.rect:
            self.canvas.coords(
                self.rect,
                self.start_canvas_x, self.start_canvas_y,
                event.x, event.y
            )
            
    def on_release(self, event):
        # Use screen coordinates for capture
        end_x = event.x_root
        end_y = event.y_root
        
        # Ensure coordinates are in correct order
        x1 = min(self.start_x, end_x)
        y1 = min(self.start_y, end_y)
        x2 = max(self.start_x, end_x)
        y2 = max(self.start_y, end_y)
        
        # Withdraw window first to hide it from screen
        self.root.withdraw()
        self.root.update()  # Force update
        
        # Schedule capture after a delay (on main thread)
        def delayed_capture():
            self.root.quit()  # Exit mainloop but keep window object
            self.callback(x1, y1, x2, y2)
            try:
                self.root.destroy()
            except:
                pass
        
        self.root.after(500, delayed_capture)  # Wait 500ms then capture
        
    def cancel(self):
        self.root.destroy()
        
    def show(self):
        self.root.mainloop()


class QRCodeReader:
    """Main application class"""
    
    def __init__(self):
        self.icon = None
        self.running = True
        
    def capture_and_decode(self):
        """Capture screen region and decode QR code"""
        def process_capture(x1, y1, x2, y2):
            try:
                # Use mss for reliable multi-monitor capture
                with mss.mss() as sct:
                    # Define the monitor region to capture
                    monitor = {
                        "top": y1, 
                        "left": x1, 
                        "width": x2 - x1, 
                        "height": y2 - y1
                    }
                    
                    # Capture the screen
                    sct_img = sct.grab(monitor)
                    
                    # Convert to PIL Image
                    screenshot = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                
                # # Save the captured image for verification
                # from datetime import datetime
                # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                # filename = f"captured_region_{timestamp}.png"
                # screenshot.save(filename)
                
                # Convert to OpenCV format
                img_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                
                # Decode QR codes
                decoded_objects = decode(img_cv)
                
                # Check if we found any QR codes
                if decoded_objects and len(decoded_objects) > 0:
                    # Get the first QR code data
                    data = decoded_objects[0].data.decode('utf-8')
                    qr_type = decoded_objects[0].type
                    self.show_result_dialog(data, qr_type)
                else:
                    # No QR code found
                    self.show_simple_message("No QR Code Found", "No QR code was detected in the selected region.")
                    
            except Exception as e:
                # Handle any errors
                import traceback
                error_msg = f"An error occurred: {str(e)}\n\n{traceback.format_exc()}"
                self.show_simple_message("Error", error_msg)
        
        # Create and show the overlay
        overlay = ScreenCaptureOverlay(process_capture)
        overlay.show()
    
    def show_result_dialog(self, data, qr_type):
        """Show result in a custom dialog with action buttons"""
        import webbrowser
        
        dialog = tk.Tk()
        dialog.title("QR Code Detected!")
        dialog.geometry("500x300")
        dialog.resizable(False, False)
        
        # Center the window
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f"500x300+{x}+{y}")
        
        # Type label
        type_label = tk.Label(dialog, text=f"Type: {qr_type}", font=('Arial', 10, 'bold'))
        type_label.pack(pady=(10, 5))
        
        # Data display with scrollbar
        frame = tk.Frame(dialog)
        frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget = tk.Text(frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, 
                             font=('Arial', 10), height=8)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_widget.insert(1.0, data)
        text_widget.config(state=tk.DISABLED)
        
        scrollbar.config(command=text_widget.yview)
        
        # Button frame
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        
        def copy_to_clipboard():
            dialog.clipboard_clear()
            dialog.clipboard_append(data)
            dialog.update()
            copy_btn.config(text="✓ Copied!")
            dialog.after(2000, lambda: copy_btn.config(text="Copy Data"))
        
        def open_url():
            webbrowser.open(data)
            dialog.destroy()
        
        # Copy button
        copy_btn = tk.Button(button_frame, text="Copy Data", command=copy_to_clipboard,
                            font=('Arial', 10), padx=20, pady=5, bg='#4CAF50', fg='white')
        copy_btn.pack(side=tk.LEFT, padx=5)
        
        # Open URL button (only if it looks like a URL)
        if data.startswith(('http://', 'https://', 'www.')):
            url_btn = tk.Button(button_frame, text="Open URL", command=open_url,
                               font=('Arial', 10), padx=20, pady=5, bg='#2196F3', fg='white')
            url_btn.pack(side=tk.LEFT, padx=5)
        
        # Close button
        close_btn = tk.Button(button_frame, text="Close", command=dialog.destroy,
                             font=('Arial', 10), padx=20, pady=5, bg='#f44336', fg='white')
        close_btn.pack(side=tk.LEFT, padx=5)
        
        dialog.mainloop()
        
    def show_simple_message(self, title, message):
        """Show a simple message box"""
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo(title, message)
        root.destroy()
        
    def start_capture(self, icon=None, item=None):
        """Start the capture mode"""
        threading.Thread(target=self.capture_and_decode, daemon=True).start()
        
    def quit_app(self, icon=None, item=None):
        """Quit the application"""
        self.running = False
        if icon:
            icon.stop()
        
    def setup_tray(self):
        """Image Load from file or bundled resource (supports PyInstaller)"""
        def resource_path(relative_path: str) -> str:
            """Get absolute path to resource, works for dev and for PyInstaller bundle."""
            if getattr(sys, 'frozen', False):
                # PyInstaller creates a temp folder and stores path in _MEIPASS
                base_path = sys._MEIPASS
            else:
                base_path = os.path.abspath(".")
            return os.path.join(base_path, relative_path)

        icon_path = resource_path(os.path.join('asset', 'icon.png'))
        icon_image = Image.open(icon_path)
        
        menu = pystray.Menu(
            item('Capture QR Code', self.start_capture),
            item('Quit', self.quit_app)
        )
        
        self.icon = pystray.Icon(
            "qr_reader",
            icon_image,
            "QR Code Reader",
            menu
        )
        
    def run(self):
        """Run the application"""
        self.setup_tray()
        print("QR Code Reader is running in system tray...")
        print("Right-click the tray icon to capture QR codes.")
        self.icon.run()


def main():
    """Main entry point"""
    app = QRCodeReader()
    app.run()


if __name__ == "__main__":
    main()
