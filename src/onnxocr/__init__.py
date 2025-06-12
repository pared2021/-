"""
ONNX Runtime DirectML based OCR engine
"""
from .ocr_engine import OCREngine
from .text_detector import TextDetector
from .text_recognizer import TextRecognizer

__all__ = ["OCREngine", "TextDetector", "TextRecognizer"]
