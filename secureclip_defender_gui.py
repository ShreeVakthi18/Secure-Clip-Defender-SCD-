import tkinter as tk
from tkinter import messagebox, scrolledtext
import win32clipboard
import re
import threading
import time
from datetime import datetime

class SecureClipDefender(tk.Tk):
    """
    A GUI application to monitor the clipboard for crypto addresses,
    sensitive data, and protect against clipboard hijacking.
    """
    def __init__(self):
        super().__init__()
        self.title("SecureClipDefender")
        self.geometry("800x600")
        self.config(bg='#2e2e2e')

        self.is_monitoring = False
        self.original_address = None
        self.last_clipboard_content = ""
        
        # Regex patterns for different types of sensitive data
        self.patterns = {
            "eth_address": re.compile(r'^(0x)?[0-9a-fA-F]{40}$'),  # Ethereum-like addresses
            "btc_address": re.compile(r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$'), # Bitcoin addresses
            "credit_card": re.compile(r'^(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|6(?:011|5[0-9][0-9])[0-9]{12}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|(?:2131|1800|35\d{3})\d{11})$'),
            "generic_password": re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')
        }

        self.create_widgets()

    def create_widgets(self):
        """Creates all the GUI elements for the application."""
        # Frame for controls
        controls_frame = tk.Frame(self, bg='#2e2e2e')
        controls_frame.pack(pady=10)

        # Start/Stop Button
        self.start_button = tk.Button(
            controls_frame, text="Start Monitoring", font=("Inter", 12, "bold"),
            bg="#4CAF50", fg="white", activebackground="#66BB6A", activeforeground="white",
            relief="raised", bd=3, command=self.toggle_monitoring
        )
        self.start_button.pack(side=tk.LEFT, padx=10)

        self.stop_button = tk.Button(
            controls_frame, text="Stop Monitoring", font=("Inter", 12, "bold"),
            bg="#F44336", fg="white", activebackground="#E57373", activeforeground="white",
            relief="raised", bd=3, command=self.toggle_monitoring, state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=10)

        # Manual Restore Button
        self.restore_button = tk.Button(
            controls_frame, text="Restore", font=("Inter", 12, "bold"),
            bg="#2196F3", fg="white", activebackground="#64B5F6", activeforeground="white",
            relief="raised", bd=3, command=self.revert_clipboard, state=tk.DISABLED
        )
        self.restore_button.pack(side=tk.LEFT, padx=10)

        # View Log Button
        self.view_log_button = tk.Button(
            controls_frame, text="View Log", font=("Inter", 12, "bold"),
            bg="#FFC107", fg="black", activebackground="#FFD54F", activeforeground="black",
            relief="raised", bd=3, command=self.view_incident_log
        )
        self.view_log_button.pack(side=tk.LEFT, padx=10)

        # Status Label
        self.status_label = tk.Label(
            self, text="Status: Not Monitoring", font=("Inter", 14, "bold"),
            bg='#2e2e2e', fg='yellow'
        )
        self.status_label.pack(pady=10)
        
        # Activity Log
        log_frame = tk.Frame(self, bg='#4a4a4a', padx=10, pady=10)
        log_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        
        log_label = tk.Label(log_frame, text="Activity Log", font=("Inter", 14, "bold"), bg='#4a4a4a', fg='white')
        log_label.pack(side=tk.TOP, anchor=tk.W)

        self.log_text = tk.Text(log_frame, bg='#3e3e3e', fg='white', font=("Inter", 10), state=tk.DISABLED)
        self.log_text.pack(expand=True, fill=tk.BOTH, pady=5)

    def log_message(self, message, color="white"):
        """Inserts a message into the log with a specific color."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n", color)
        self.log_text.tag_config(color, foreground=color)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def update_status(self, message, color='yellow'):
        """Updates the status label with a message and color."""
        self.status_label.config(text=f"Status: {message}", fg=color)
        
    def toggle_monitoring(self):
        """Starts or stops the clipboard monitoring process."""
        self.is_monitoring = not self.is_monitoring
        if self.is_monitoring:
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.update_status("Monitoring Active", 'green')
            self.log_message("Monitoring started.")
            # Start the monitoring function in a separate thread
            self.monitor_thread = threading.Thread(target=self.monitor_clipboard, daemon=True)
            self.monitor_thread.start()
        else:
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.restore_button.config(state=tk.DISABLED)
            self.update_status("Not Monitoring", 'yellow')
            self.log_message("Monitoring stopped.")

    def get_clipboard_text(self):
        """Safely gets text from the clipboard."""
        try:
            win32clipboard.OpenClipboard()
            if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_UNICODETEXT):
                content = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
            else:
                content = None
            win32clipboard.CloseClipboard()
            return content
        except Exception as e:
            # Silently fail if clipboard is not accessible
            return None

    def monitor_clipboard(self):
        """Continuously checks for changes in the clipboard."""
        while self.is_monitoring:
            clipboard_content = self.get_clipboard_text()
            if clipboard_content and clipboard_content != self.last_clipboard_content:
                self.last_clipboard_content = clipboard_content
                # Add a small delay to ensure the clipboard is stable
                time.sleep(0.1) 
                self.process_clipboard(clipboard_content)
            
            time.sleep(0.5) # Check every half-second

    def process_clipboard(self, content):
        """Analyzes clipboard content and reacts accordingly."""
        if not isinstance(content, str):
            # Not text, so we ignore
            self.original_address = None
            self.restore_button.config(state=tk.DISABLED)
            return

        # Strip any leading/trailing whitespace before processing
        content = content.strip()

        crypto_type = None
        if self.patterns["eth_address"].match(content):
            crypto_type = "ETH"
        elif self.patterns["btc_address"].match(content):
            crypto_type = "BTC"

        if crypto_type:
            self.log_message(f"Detected a new crypto address ({crypto_type}): {content}", "yellow")
            if self.original_address is None:
                self.original_address = content
                self.update_status("Crypto Address Detected", 'yellow')
                self.log_message("Monitoring for potential hijacking...", "orange")
            elif content != self.original_address:
                self.update_status("Hijack Detected! Click Restore to revert.", 'red')
                self.log_message(f"🚨 Potential hijacking detected! The address has been changed to '{content}'.", "red")
                self.restore_button.config(state=tk.NORMAL)
                self.log_hijack_incident(self.original_address, content, crypto_type)

        elif self.patterns["credit_card"].match(content) or self.patterns["generic_password"].match(content):
            data_type = "Credit Card" if self.patterns["credit_card"].match(content) else "Generic Password"
            self.log_message(f"Detected sensitive data ({data_type}): {content}", "purple")
            self.update_status("Sensitive Data Detected!", 'purple')
            self.log_message(f"Sensitive data ({data_type}) has been copied. Please be careful with this information.", "magenta")
            # Reset any hijack-related state
            self.original_address = None
            self.restore_button.config(state=tk.DISABLED)

        else:
            # If the content is not a crypto address or sensitive data, we reset the state
            if self.original_address is not None:
                self.log_message("Clipboard content changed to non-crypto data. Hijack address reset.", "blue")
            self.original_address = None
            self.restore_button.config(state=tk.DISABLED)
            self.update_status("Monitoring Active", 'green')
    
    def log_hijack_incident(self, original, hijacked, crypto_type):
        """Logs a hijack incident to a local file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - Type: {crypto_type} | Original: {original} | Hijacked: {hijacked}\n"
        try:
            with open("hijack_incidents.log", "a") as f:
                f.write(log_entry)
            self.log_message("Hijack incident logged to hijack_incidents.log", "green")
        except Exception as e:
            self.log_message(f"Error writing to log file: {e}", "red")

    def view_incident_log(self):
        """Opens a new window to display the contents of the log file."""
        log_window = tk.Toplevel(self)
        log_window.title("Hijack Incident Log")
        log_window.geometry("600x400")
        log_window.config(bg='#2e2e2e')

        log_label = tk.Label(log_window, text="Hijack Incidents", font=("Inter", 14, "bold"), bg='#2e2e2e', fg='white')
        log_label.pack(pady=10)

        log_text_widget = scrolledtext.ScrolledText(log_window, bg='#3e3e3e', fg='white', font=("Inter", 10), wrap=tk.WORD)
        log_text_widget.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        try:
            with open("hijack_incidents.log", "r") as f:
                log_content = f.read()
                log_text_widget.insert(tk.END, log_content)
        except FileNotFoundError:
            log_text_widget.insert(tk.END, "No hijack incidents have been logged yet.")
        except Exception as e:
            log_text_widget.insert(tk.END, f"Error reading log file: {e}")

        log_text_widget.config(state=tk.DISABLED)

    def revert_clipboard(self):
        """Reverts the clipboard to the original address."""
        if self.original_address:
            try:
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(self.original_address)
                win32clipboard.CloseClipboard()
                self.log_message(f"Clipboard reverted to original address: {self.original_address}", "green")
                self.update_status("Restored to Original", "green")
                self.restore_button.config(state=tk.DISABLED)
                # We can reset the original address after a successful restore
                self.original_address = None
            except Exception as e:
                self.log_message(f"Error reverting clipboard: {e}", "red")

if __name__ == "__main__":
    app = SecureClipDefender()
    app.mainloop()
