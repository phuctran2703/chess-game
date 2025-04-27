import sys

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "gui":
        from gui.chess_gui import ChessGUI
        app = ChessGUI()
        app.mainloop()
    else:
        print("Chess Coding Adventure CLI mode (chưa triển khai)")
        print("Chạy: python main.py gui để mở giao diện đồ họa.")

if __name__ == "__main__":
    main()
