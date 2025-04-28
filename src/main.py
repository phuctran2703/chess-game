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
        if sys.argv[1] == '--ai-visualizer':
            # Run with AI visualization (Human vs AI with visualization)
            print("Starting Chess game with AI visualization...")
            app = AIVisualizerGUI(root)
            root.title("Chess Game - AI Visualizer")
        elif sys.argv[1] == '--ai-vs-ai':
            # Run Agent vs Agent mode
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
    selection_window = tk.Toplevel(root)
    selection_window.title("Chess Game - Mode Selection")
    selection_window.geometry("500x500")
    selection_window.resizable(False, False)
    selection_window.protocol("WM_DELETE_WINDOW", root.destroy)  # Close app if dialog is closed
    
    # Center the window
    selection_window.geometry("+%d+%d" % (
        root.winfo_screenwidth() // 2 - 250,
        root.winfo_screenheight() // 2 - 300))
    
    # Title label
    title_label = tk.Label(selection_window, text="Chess Game", font=("Arial", 24, "bold"))
    title_label.pack(pady=20)
    
    # Mode selection frame
    selection_frame = tk.Frame(selection_window)
    selection_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)
    
    # Regular Chess mode
    normal_button = tk.Button(
        selection_frame, 
        text="Chơi Thường", 
        font=("Arial", 14),
        bg="#4CAF50", fg="white",
        height=2,
        command=lambda: launch_mode(root, selection_window, "normal")
    )
    normal_button.pack(fill=tk.X, pady=10)
    
    # Human vs AI with visualization
    ai_viz_button = tk.Button(
        selection_frame, 
        text="Người vs Agent", 
        font=("Arial", 14),
        bg="#2196F3", fg="white",
        height=2,
        command=lambda: launch_mode(root, selection_window, "ai-viz")
    )
    ai_viz_button.pack(fill=tk.X, pady=10)
    
    # Agent vs Agent mode
    ai_vs_ai_button = tk.Button(
        selection_frame, 
        text="Agent vs Agent", 
        font=("Arial", 14),
        bg="#9C27B0", fg="white",
        height=2,
        command=lambda: launch_mode(root, selection_window, "ai-vs-ai")
    )
    ai_vs_ai_button.pack(fill=tk.X, pady=10)
    
    # Exit button
    exit_button = tk.Button(
        selection_frame, 
        text="Thoát", 
        font=("Arial", 14),
        bg="#f44336", fg="white",
        height=2,
        command=root.destroy
    )
    exit_button.pack(fill=tk.X, pady=10)

def launch_mode(root, selection_window, mode):
    """
    Launch the selected game mode
    """
    selection_window.destroy()
    root.deiconify()  # Show the main window
    
    # Cấu hình màn hình phóng to
    root.state('zoomed')  # Phóng to màn hình trên Windows
    
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
