import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

print("Testing imports...")
try:
    import main
    import db.database
    import ui.entry_widget
    import ui.query_widget
    import ui.main_window
    print("Imports successful!")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)
