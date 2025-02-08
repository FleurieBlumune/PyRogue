"""Game launcher with error handling."""

import sys
import traceback

def main():
    try:
        # Import and run game properly
        from main import main as game_main
        game_main()
    except Exception as e:
        print("\nError occurred:", file=sys.stderr)
        print(f"{type(e).__name__}: {e}", file=sys.stderr)
        traceback.print_exc()
        
        with open('error.log', 'w') as f:
            traceback.print_exc(file=f)
        
        print("\nError has been logged to error.log")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
