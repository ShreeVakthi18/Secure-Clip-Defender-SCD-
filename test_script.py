import time
import win32clipboard

def set_clipboard_text(text):
    """
    Helper function to set the clipboard content.
    """
    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        # Set the text with a small delay for stability
        win32clipboard.SetClipboardText(text)
        win32clipboard.CloseClipboard()
        print(f"Clipboard set to: '{text}'")
    except Exception as e:
        print(f"Error setting clipboard: {e}")

def run_test_scenario():
    """
    Runs a series of clipboard changes to test SecureClipDefender.
    """
    print("Starting clipboard test scenario...")
    print("Please ensure SecureClipDefender is running and monitoring is active.")
    time.sleep(3)

    # Scenario 1: Copying a crypto address (ETH)
    print("\n--- Scenario 1: Crypto Address (ETH) ---")
    eth_address = "0x742d35Cc4d2948278E6e2d93eD46C2cE8284C27f"
    set_clipboard_text(eth_address)
    time.sleep(5)

    # Scenario 2: Simulating an ETH address hijack
    print("\n--- Scenario 2: ETH Hijack ---")
    hijacked_eth_address = "0x89D24A6b4CcB1b6fAA2625fE562b39f3Bb9cAb8a"
    set_clipboard_text(hijacked_eth_address)
    time.sleep(5)

    # Scenario 3: Copying a different type of crypto address (BTC)
    print("\n--- Scenario 3: Crypto Address (BTC) ---")
    btc_address = "1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2"
    set_clipboard_text(btc_address)
    time.sleep(5)
    
    # Scenario 4: Simulating a BTC address hijack
    print("\n--- Scenario 4: BTC Hijack ---")
    hijacked_btc_address = "1HB5k98JjR18B5LwF6r83KzTj97pC2k2fJ"
    set_clipboard_text(hijacked_btc_address)
    time.sleep(5)

    # Scenario 5: Copying a credit card number (sensitive data)
    print("\n--- Scenario 5: Sensitive Data (Credit Card) ---")
    cc_number = "4111222233334444"
    set_clipboard_text(cc_number)
    time.sleep(5)

    # Scenario 6: Copying a generic password
    print("\n--- Scenario 6: Sensitive Data (Password) ---")
    password = "My-secure-P@ssword123"
    set_clipboard_text(password)
    time.sleep(5)
    
    # Scenario 7: Copying normal text (to reset state)
    print("\n--- Scenario 7: Normal Text ---")
    set_clipboard_text("This is some normal text.")
    time.sleep(5)

    print("\nTest scenario complete.")

if __name__ == "__main__":
    run_test_scenario()
