"""
Chess piece image handling for the GUI.
This module loads and manages chess piece images.
"""
import os
import tkinter as tk
from PIL import Image, ImageTk
from src.core.Board.piece import *

class PieceImageManager:
    """
    Manages the loading and caching of chess piece images
    """
    def __init__(self, size=80):
        self.size = size
        self.images = {}
        self.default_font = ('Arial', int(size * 0.7), 'bold')
        self.piece_to_file = {
            # White pieces
            WHITE_PAWN: "wp",
            WHITE_KNIGHT: "wn", 
            WHITE_BISHOP: "wb",
            WHITE_ROOK: "wr",
            WHITE_QUEEN: "wq",
            WHITE_KING: "wk",
            
            # Black pieces
            BLACK_PAWN: "bp",
            BLACK_KNIGHT: "bn",
            BLACK_BISHOP: "bb",
            BLACK_ROOK: "br",
            BLACK_QUEEN: "bq",
            BLACK_KING: "bk"
        }
        
        # Load images
        self.load_images()
    
    def load_images(self):
        """
        Load chess piece images from assets directory
        """
        # Check if the assets directory exists
        assets_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "pieces")
        images_available = os.path.exists(assets_path)
        
        for piece_code, filename in self.piece_to_file.items():
            try:
                if images_available:
                    # Path to the piece image
                    image_path = os.path.join(assets_path, f"{filename}.png")
                    
                    if os.path.exists(image_path):
                        # Load and resize the image
                        img = Image.open(image_path)
                        img = img.resize((self.size, self.size), Image.LANCZOS)
                        
                        # Create the PhotoImage from the loaded image
                        self.images[piece_code] = ImageTk.PhotoImage(img)
                        continue
            except Exception as e:
                print(f"Error loading image for {filename}: {e}")
            
            # If image loading fails or images aren't available, use fallback text
            self.images[piece_code] = None
    
    def resize(self, new_size):
        """
        Resize all piece images
        """
        if self.size == new_size:
            return
        
        self.size = new_size
        self.default_font = ('Arial', int(new_size * 0.7), 'bold')
        # Reload images at new size
        self.load_images()
    
    def get_image(self, piece):
        """
        Get the image for a specific piece
        Returns the image or None if not available
        """
        if piece == NONE:
            return None
        return self.images.get(piece)
    
    def get_fallback_text(self, piece):
        """
        Get fallback text representation for a piece
        Used when images are not available
        """
        if piece == NONE:
            return ""
            
        symbol = get_symbol(piece)
        # Make black pieces silver with a white outline for better visibility
        if is_white(piece):
            color = "black"
            outline = ""
            font = self.default_font
        else:
            color = "#E0E0E0"  # Light silver color for black pieces
            outline = "white"
            font = (self.default_font[0], self.default_font[1], 'bold')
        return (symbol, color, font)
