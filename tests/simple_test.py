print("Hello, this is a simple test!")
try:
    import numpy as np
    print(f"NumPy version: {np.__version__}")
except ImportError:
    print("NumPy not available")

try:
    import cv2
    print(f"OpenCV version: {cv2.__version__}")
except ImportError:
    print("OpenCV not available")

try:
    from PyQt6.QtWidgets import QApplication
    print("PyQt6 is available")
except ImportError:
    print("PyQt6 not available")

print("Test completed!")