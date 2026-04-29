import win32clipboard # For Windows clipboard access
import time           # For pausing the script
import sys            # For printing to standard error

def get_clipboard_text():
    """
    Retrieves the current text content from the clipboard.
    Returns an empty string if the clipboard is empty or contains non-text data.
    Handles common errors during clipboard access.
    """
    try:
        # Open the clipboard for read access. This locks it, preventing other apps from modifying it.
        win32clipboard.OpenClipboard()

        # Check if text data is available (CF_UNICODETEXT is for Unicode text)
        if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_UNICODETEXT):
            # Get the clipboard data as text
            data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
            return data
        else:
            return "" # No text data available on the clipboard
    except Exception as e:
        # Catch any exceptions that occur during clipboard operations (e.g., another app has it open)
        print(f"Error accessing clipboard: {e}", file=sys.stderr)
        return "" # Return empty string on error
    finally:
        # Always try to close the clipboard to release the lock
        try:
            win32clipboard.CloseClipboard()
        except Exception as e:
            # This can happen if the clipboard was already closed or not opened successfully
            # We can often ignore these errors during close, but good to be aware.
            print(f"Error closing clipboard: {e}", file=sys.stderr)

def monitor_clipboard():
    """
    Continuously monitors the clipboard for changes and prints new text content
    to the console. It uses the clipboard sequence number for efficient detection.
    """
    print("--- SecureClip Defender CLI: Clipboard Monitor ---")
    print("Monitoring clipboard... Press Ctrl+C to stop.")

    # Initialize variables to track clipboard state
    last_sequence_number = 0
    last_clipboard_content = "" # Stores the last *valid* text content we processed

    while True:
        try:
            # Get the current clipboard sequence number. This number increments
            # every time the content of the clipboard changes.
            current_sequence_number = win32clipboard.GetClipboardSequenceNumber()

            # If the sequence number has changed, the clipboard content has been updated
            if current_sequence_number != last_sequence_number:
                new_content = get_clipboard_text() # Get the new content

                # Only process if:
                # 1. new_content is not empty (avoid processing empty clipboard changes)
                # 2. new_content is actually different from the last *valid* content we saw
                if new_content and new_content != last_clipboard_content:
                    print(f"\n[Clipboard Changed Detected] New Content: '{new_content}'")
                    last_clipboard_content = new_content # Update our stored content
                elif not new_content and last_clipboard_content:
                    # If content became empty after previously holding content, notify
                    print(f"\n[Clipboard Cleared/Changed] Content is now empty or non-text.")
                    last_clipboard_content = "" # Clear our stored content

                # Always update the last sequence number, even if content was empty
                last_sequence_number = current_sequence_number

            time.sleep(0.5) # Pause for 500 milliseconds before checking again (reduces CPU usage)

        except KeyboardInterrupt:
            # Catch Ctrl+C to gracefully stop the monitoring loop
            print("\nMonitoring stopped by user.")
            break # Exit the while loop
        except Exception as e:
            # Catch any other unexpected errors during the monitoring loop
            print(f"An unexpected error occurred during monitoring: {e}", file=sys.stderr)
            time.sleep(1) # Wait longer on error to prevent rapid error looping

# This ensures that monitor_clipboard() only runs when the script is executed directly
if __name__ == "__main__":
    monitor_clipboard()