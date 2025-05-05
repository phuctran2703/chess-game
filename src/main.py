from src.ui.human_vs_human_gui import ChessGUI
from src.ui.agent_vs_human_gui import AIVisualizerGUI
from src.ui.agent_vs_agent_gui import AgentvsAgentGUI
import tkinter as tk
import sys


def main():
    """
    Main entry point for the chess game application
    """
    root = tk.Tk()

    # Determine which mode to run based on command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--ai-visualizer":
            # Run with AI visualization (Human vs AI with visualization)
            print("Starting Chess game with AI visualization...")
            app = AIVisualizerGUI(root)
            root.title("Chess Game - AI Visualizer")
        elif sys.argv[1] == "--ai-vs-ai":
            print("Starting Agent vs Agent Chess game...")
            app = AgentvsAgentGUI(root)
            root.title("Chess Game - Agent vs Agent")
        else:
            # Unknown argument, run normal mode
            print(f"Unknown argument: {sys.argv[1]}")
            print("Starting normal Chess game...")
            app = ChessGUI(root)
            root.title("Chess Game")
    else:
        # No arguments, show mode selection dialog
        root.withdraw()  # Hide the main window temporarily
        show_mode_selection(root)

    root.mainloop()


def show_mode_selection(root):
    """
    Show a dialog to let the user select which game mode to run
    """
    # Import necessary modules for improved UI
    import tkinter.font as tkfont

    # Setup the selection window with a dark theme
    selection_window = tk.Toplevel(root)
    selection_window.title("Chess Game - Mode Selection")
    selection_window.geometry("700x650")
    selection_window.resizable(False, False)
    selection_window.protocol("WM_DELETE_WINDOW", root.destroy)

    # Set dark background color
    selection_window.configure(bg="#1E1E1E")

    # Center the window
    selection_window.geometry(
        "+%d+%d"
        % (root.winfo_screenwidth() // 2 - 350, root.winfo_screenheight() // 2 - 325)
    )

    # Create a frame for the content
    main_frame = tk.Frame(selection_window, bg="#1E1E1E")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

    # Create a chess icon using native tkinter canvas - centered and properly balanced
    chess_icon = tk.Canvas(
        main_frame, width=160, height=160, bg="#1E1E1E", highlightthickness=0
    )
    chess_icon.pack(pady=(0, 10))

    # Draw chess board pattern (simplified) - perfectly centered on canvas
    square_size = 14
    board_size = square_size * 8
    offset_x = (160 - board_size) // 2  # Center horizontally
    offset_y = (160 - board_size) // 2  # Center vertically

    # Draw board with clear colors
    for row in range(8):
        for col in range(8):
            color = "#FFFFFF" if (row + col) % 2 == 0 else "#222222"
            chess_icon.create_rectangle(
                col * square_size + offset_x,
                row * square_size + offset_y,
                (col + 1) * square_size + offset_x,
                (row + 1) * square_size + offset_y,
                fill=color,
                outline="",
            )

    # Draw an elegant circular border around the board for visual balance
    circle_padding = 10
    chess_icon.create_oval(
        offset_x - circle_padding,
        offset_y - circle_padding,
        offset_x + board_size + circle_padding,
        offset_y + board_size + circle_padding,
        outline="#CCCCCC",
        width=2,
    )

    # Draw a more balanced knight silhouette - centered on the board
    knight_base_x = offset_x + board_size / 2  # Center x position
    knight_base_y = offset_y + board_size / 2  # Center y position

    # Scaled knight coordinates for better visibility
    knight_points = [
        knight_base_x - 5,
        knight_base_y - 15,  # top of head
        knight_base_x + 5,
        knight_base_y - 12,  # top right of head
        knight_base_x + 10,
        knight_base_y - 5,  # nose
        knight_base_x + 5,
        knight_base_y,  # mouth
        knight_base_x + 12,
        knight_base_y + 10,  # back of neck
        knight_base_x + 5,
        knight_base_y + 15,  # bottom back
        knight_base_x,
        knight_base_y + 15,  # bottom middle
        knight_base_x - 10,
        knight_base_y + 10,  # front legs
        knight_base_x - 12,
        knight_base_y,  # chest
        knight_base_x - 10,
        knight_base_y - 10,  # front of face
    ]
    chess_icon.create_polygon(knight_points, fill="#000000", outline="")

    # Create more prominent title with enhanced clarity
    title_font = tkfont.Font(family="Helvetica", size=42, weight="bold")
    title_label = tk.Label(
        main_frame,
        text="Chess Game",
        font=title_font,
        fg="#FFFFFF",  # Pure white for maximum contrast
        bg="#1E1E1E",
    )
    title_label.pack(pady=(10, 20))

    # Create a more visible description with better contrast
    desc_font = tkfont.Font(family="Helvetica", size=16, weight="bold")
    desc_label = tk.Label(
        main_frame,
        text="Select your preferred game mode",
        font=desc_font,
        fg="#DDDDDD",  # Lighter color for better visibility
        bg="#1E1E1E",
    )
    desc_label.pack(pady=(0, 30))

    # Create a styled frame for buttons
    button_frame = tk.Frame(main_frame, bg="#1E1E1E", padx=50)
    button_frame.pack(fill=tk.X, expand=True)

    # Simple button style with identical appearance for all buttons
    button_style = {
        "font": ("Arial", 16),  # Moderate size that won't cause text wrapping
        "borderwidth": 1,
        "pady": 8,
        "relief": tk.RAISED,
        "cursor": "hand2",
    }

    # Common button properties for all game mode buttons
    common_button_props = {
        "bg": "#EEEEEE",
        "fg": "#000000",
        "activebackground": "#D5D5D5",
        "activeforeground": "#000000",
    }

    # Use identical styling for all buttons
    button_texts = ["Regular Game", "Human vs Agent", "Agent vs Agent"]
    button_commands = [
        lambda: launch_mode(root, selection_window, "normal"),
        lambda: launch_mode(root, selection_window, "ai-viz"),
        lambda: launch_mode(root, selection_window, "ai-vs-ai"),
    ]

    # Create the game mode buttons with identical styling
    for text, cmd in zip(button_texts, button_commands):
        btn = tk.Button(
            button_frame, text=text, command=cmd, **common_button_props, **button_style
        )
        btn.pack(fill=tk.X, pady=10, ipady=10)

    # Exit button - same styling but with red text
    exit_button = tk.Button(
        button_frame,
        text="Exit",
        bg="#EEEEEE",
        fg="#B71C1C",  # Red text to indicate exit
        activebackground="#D5D5D5",
        activeforeground="#B71C1C",
        command=root.destroy,
        **button_style,
    )
    exit_button.pack(fill=tk.X, pady=10, ipady=10)

    # Add a footer with version info
    footer_frame = tk.Frame(main_frame, bg="#1E1E1E")
    footer_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=20)

    version_label = tk.Label(
        footer_frame, text="v1.0", font=("Helvetica", 10), fg="#555555", bg="#1E1E1E"
    )
    version_label.pack(side=tk.RIGHT, padx=5)


def launch_mode(root, selection_window, mode):
    """
    Launch the selected game mode
    """
    selection_window.destroy()
    root.deiconify()  # Show the main window

    # Configure fullscreen
    root.state("zoomed")  # Maximize screen on Windows

    if mode == "normal":
        app = ChessGUI(root)
        root.title("Chess Game")
    elif mode == "ai-viz":
        app = AIVisualizerGUI(root)
        root.title("Chess Game - AI Visualizer")
    elif mode == "ai-vs-ai":
        app = AgentvsAgentGUI(root)
        root.title("Chess Game - Agent vs Agent")


if __name__ == "__main__":
    main()
