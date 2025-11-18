import tkinter as tk
from tkinter import messagebox, simpledialog
from game_logic import Game
import math

class GameGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Snake and Ladder Game")
        self.geometry("1000x700")
        self.game = None
        self.player_colors = ["#FFD700", "#6495ED", "#DC143C", "#8A2BE2"]
        self.is_ai_game = False
        self.player_names = []
        self.player_stat_frames = []
        self.ai_thinking = False

        self.create_widgets()


    def create_widgets(self):
        # Frame for board size and player count input
        self.setup_frame = tk.Frame(self)
        self.setup_frame.pack(pady=10)
        tk.Label(self.setup_frame, text="Board Size (6-12):").pack(side=tk.LEFT)
        self.size_entry = tk.Entry(self.setup_frame, width=5)
        self.size_entry.insert(0, "10")  # Default value
        self.size_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(self.setup_frame, text="Players (1-4):").pack(side=tk.LEFT)
        self.players_entry = tk.Entry(self.setup_frame, width=5)
        self.players_entry.insert(0, "2")  # Default value
        self.players_entry.pack(side=tk.LEFT)
        
        self.start_button = tk.Button(self.setup_frame, text="Start Game", command=self.start_game)
        self.start_button.pack(side=tk.LEFT, padx=10)

        # Main game area with player stats on sides
        self.game_container = tk.Frame(self)
        self.game_container.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Left player stats panel
        self.left_panel = tk.Frame(self.game_container, width=150, relief=tk.RIDGE, borderwidth=2)
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 5))
        self.left_panel.pack_propagate(False)

        # Center - Board display
        self.board_frame = tk.Frame(self.game_container, relief=tk.SUNKEN, borderwidth=2)
        self.board_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.board_canvas = tk.Canvas(self.board_frame, bg="white", width=500, height=500)
        self.board_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind canvas resize event
        self.board_canvas.bind('<Configure>', self.on_canvas_resize)

        # Right player stats panel
        self.right_panel = tk.Frame(self.game_container, width=150, relief=tk.RIDGE, borderwidth=2)
        self.right_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(5, 0))
        self.right_panel.pack_propagate(False)

        # Frame for game controls
        self.control_frame = tk.Frame(self)
        self.control_frame.pack(pady=10)

        self.roll_button = tk.Button(self.control_frame, text="Roll Dice", command=self.roll_dice,
                                     state=tk.DISABLED, font=("Helvetica", 12, "bold"))
        self.roll_button.pack(side=tk.LEFT, padx=10)


        # Frame for the answer input
        self.answer_frame = tk.Frame(self)
        self.answer_frame.pack(pady=10)
        tk.Label(self.answer_frame, text="Enter your guess for minimum throws:").pack(side=tk.LEFT)
        self.answer_entry = tk.Entry(self.answer_frame, width=5)
        self.answer_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.submit_button = tk.Button(self.answer_frame, text="Submit", command=self.check_answer)
        self.submit_button.pack(side=tk.LEFT)
        self.answer_frame.pack_forget()

    def on_canvas_resize(self, event):
        """Redraw board when canvas is resized."""
        if self.game:
            self.draw_board()

    def start_game(self):
        try:
            n = int(self.size_entry.get())
            num_players = int(self.players_entry.get())
            if not (6 <= n <= 12):
                messagebox.showerror("Error", "Board size must be between 6 and 12.")
                return
            if not (1 <= num_players <= 4):
                messagebox.showerror("Error", "Number of players must be between 1 and 4.")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid board size or number of players.")
            return

        # Check if single player mode (AI opponent)
        if num_players == 1:
            self.is_ai_game = True
            num_players = 2  # Player vs AI
            messagebox.showinfo("Single Player Mode", "You will play against an AI opponent!")
        else:
            self.is_ai_game = False

        self.game = Game(n, num_players)

        # Clear previous player stat frames
        for widget in self.left_panel.winfo_children():
            widget.destroy()
        for widget in self.right_panel.winfo_children():
            widget.destroy()
        self.player_stat_frames = []

        # Create player stat displays
        self.create_player_stats()

        # Wait for canvas to be properly sized
        self.update_idletasks()
        self.draw_board()
        self.update_player_stats()
        self.roll_button.config(state=tk.NORMAL)
        self.answer_frame.pack_forget()

        # If AI starts first, make its move
        if self.is_ai_game and self.game.current_player == 1:
            self.after(500, self.ai_move)

    def create_player_stats(self):
        """Create stat displays for each player in the side panels."""
        panels = [self.left_panel, self.right_panel, self.left_panel, self.right_panel]

        for i in range(self.game.num_players):
            # Determine which panel to use
            parent = panels[i]

            # Create frame for this player
            frame = tk.Frame(parent, relief=tk.RAISED, borderwidth=3,
                           bg=self.player_colors[i], padx=10, pady=10)
            frame.pack(pady=10, padx=5, fill=tk.BOTH, expand=True)

            # Player name/title
            if self.is_ai_game and i == 1:
                player_name = "AI Opponent"
            else:
                player_name = f"Player {i + 1}"

            title = tk.Label(frame, text=player_name, font=("Helvetica", 14, "bold"),
                           bg=self.player_colors[i], fg="black")
            title.pack(pady=(0, 10))

            # Status indicator
            status_frame = tk.Frame(frame, bg=self.player_colors[i])
            status_frame.pack(fill=tk.X, pady=5)
            tk.Label(status_frame, text="Status:", font=("Helvetica", 10, "bold"),
                    bg=self.player_colors[i]).pack(anchor=tk.W)
            status_label = tk.Label(status_frame, text="Waiting", font=("Helvetica", 10),
                                   bg=self.player_colors[i], fg="gray")
            status_label.pack(anchor=tk.W)

            # Position
            pos_frame = tk.Frame(frame, bg=self.player_colors[i])
            pos_frame.pack(fill=tk.X, pady=5)
            tk.Label(pos_frame, text="Position:", font=("Helvetica", 10, "bold"),
                    bg=self.player_colors[i]).pack(anchor=tk.W)
            pos_label = tk.Label(pos_frame, text="1", font=("Helvetica", 12),
                                bg=self.player_colors[i])
            pos_label.pack(anchor=tk.W)

            # Throws
            throws_frame = tk.Frame(frame, bg=self.player_colors[i])
            throws_frame.pack(fill=tk.X, pady=5)
            tk.Label(throws_frame, text="Throws:", font=("Helvetica", 10, "bold"),
                    bg=self.player_colors[i]).pack(anchor=tk.W)
            throws_label = tk.Label(throws_frame, text="0", font=("Helvetica", 12),
                                   bg=self.player_colors[i])
            throws_label.pack(anchor=tk.W)

            # Last dice roll
            dice_frame = tk.Frame(frame, bg=self.player_colors[i])
            dice_frame.pack(fill=tk.X, pady=5)
            tk.Label(dice_frame, text="Last Roll:", font=("Helvetica", 10, "bold"),
                    bg=self.player_colors[i]).pack(anchor=tk.W)
            dice_label = tk.Label(dice_frame, text="-", font=("Helvetica", 12),
                                 bg=self.player_colors[i])
            dice_label.pack(anchor=tk.W)

            # Store references
            self.player_stat_frames.append({
                'frame': frame,
                'status': status_label,
                'position': pos_label,
                'throws': throws_label,
                'dice': dice_label
            })

    def draw_board(self):
        self.board_canvas.delete("all")

        # Ensure canvas has proper dimensions
        self.board_canvas.update_idletasks()
        canvas_width = self.board_canvas.winfo_width()
        canvas_height = self.board_canvas.winfo_height()
        
        # Minimum size check
        if canvas_width < 100 or canvas_height < 100:
            canvas_width = 600
            canvas_height = 400
        
        cell_width = canvas_width / self.game.n
        cell_height = canvas_height / self.game.n
        
        colors = ["#FFDDC1", "#FFFFE0", "#BEEB9F", "#A7D8DE", "#E0BBE4", 
                 "#FFDAC1", "#FFB7B2", "#FFD8B1", "#B5EAD7", "#C7CEEA"]

        # Draw cells
        for i in range(1, self.game.board_size + 1):
            row = (i - 1) // self.game.n
            col = (i - 1) % self.game.n
            
            if row % 2 != 0:
                col = self.game.n - 1 - col

            x1 = col * cell_width
            y1 = canvas_height - (row + 1) * cell_height
            x2 = x1 + cell_width
            y2 = y1 + cell_height
            
            self.board_canvas.create_rectangle(x1, y1, x2, y2, 
                                              fill=colors[(i - 1) % len(colors)], 
                                              outline="black", width=2)
            self.board_canvas.create_text(x1 + cell_width / 2, y1 + cell_height / 2, 
                                         text=str(i), font=("Helvetica", 10, "bold"))

        # Draw snakes and ladders
        for start, end in self.game.snakes.items():
            self.draw_snake(start, end, cell_width, cell_height, canvas_height)
        for start, end in self.game.ladders.items():
            self.draw_ladder(start, end, cell_width, cell_height, canvas_height)

        # Draw players
        for i in range(self.game.num_players):
            self.draw_player(i, cell_width, cell_height, canvas_height)

    def get_cell_center(self, pos, cell_width, cell_height, canvas_height):
        row = (pos - 1) // self.game.n
        col = (pos - 1) % self.game.n
        if row % 2 != 0:
            col = self.game.n - 1 - col
        
        x = col * cell_width + cell_width / 2
        y = canvas_height - (row * cell_height + cell_height / 2)
        return x, y

    def draw_snake(self, start, end, cell_width, cell_height, canvas_height):
        x1, y1 = self.get_cell_center(start, cell_width, cell_height, canvas_height)
        x2, y2 = self.get_cell_center(end, cell_width, cell_height, canvas_height)

        # Draw a curvy snake body with multiple segments
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        num_segments = max(5, int(distance / 20))
        
        points = []
        for i in range(num_segments + 1):
            t = i / num_segments
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)
            
            # Add wave effect perpendicular to the line
            angle = math.atan2(y2 - y1, x2 - x1)
            wave_offset = math.sin(t * math.pi * 3) * 15
            x += wave_offset * math.sin(angle + math.pi / 2)
            y -= wave_offset * math.cos(angle + math.pi / 2)
            
            points.extend([x, y])
        
        # Draw snake body with gradient effect
        self.board_canvas.create_line(points, fill="#2E7D32", width=8, 
                                      smooth=True, capstyle=tk.ROUND)
        self.board_canvas.create_line(points, fill="#4CAF50", width=6, 
                                      smooth=True, capstyle=tk.ROUND)
        
        # Draw snake head at the end position
        head_size = 12
        self.board_canvas.create_oval(x2 - head_size, y2 - head_size, 
                                     x2 + head_size, y2 + head_size, 
                                     fill="#1B5E20", outline="#0D47A1", width=2)
        
        # Eyes
        eye_offset = 5
        angle = math.atan2(y2 - y1, x2 - x1)
        eye1_x = x2 + eye_offset * math.cos(angle + math.pi / 4)
        eye1_y = y2 + eye_offset * math.sin(angle + math.pi / 4)
        eye2_x = x2 + eye_offset * math.cos(angle - math.pi / 4)
        eye2_y = y2 + eye_offset * math.sin(angle - math.pi / 4)
        
        self.board_canvas.create_oval(eye1_x - 2, eye1_y - 2, eye1_x + 2, eye1_y + 2, 
                                     fill="red", outline="")
        self.board_canvas.create_oval(eye2_x - 2, eye2_y - 2, eye2_x + 2, eye2_y + 2, 
                                     fill="red", outline="")
        
        # Draw tail at start position with arrow
        tail_size = 8
        self.board_canvas.create_oval(x1 - tail_size, y1 - tail_size, 
                                     x1 + tail_size, y1 + tail_size, 
                                     fill="#66BB6A", outline="#2E7D32", width=2)

    def draw_ladder(self, start, end, cell_width, cell_height, canvas_height):
        x1, y1 = self.get_cell_center(start, cell_width, cell_height, canvas_height)
        x2, y2 = self.get_cell_center(end, cell_width, cell_height, canvas_height)

        # Draw parallel lines for ladder
        angle = math.atan2(y2 - y1, x2 - x1)
        offset = 3
        dx = offset * math.sin(angle)
        dy = -offset * math.cos(angle)
        
        self.board_canvas.create_line(x1 + dx, y1 + dy, x2 + dx, y2 + dy, 
                                      fill="brown", width=3)
        self.board_canvas.create_line(x1 - dx, y1 - dy, x2 - dx, y2 - dy, 
                                      fill="brown", width=3)
        
        # Draw rungs
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        num_rungs = max(3, int(distance / 30))
        for i in range(1, num_rungs):
            t = i / num_rungs
            rx = x1 + t * (x2 - x1)
            ry = y1 + t * (y2 - y1)
            self.board_canvas.create_line(rx + dx, ry + dy, rx - dx, ry - dy, 
                                         fill="brown", width=2)

    def draw_player(self, player_index, cell_width, cell_height, canvas_height):
        pos = self.game.player_positions[player_index]
        x, y = self.get_cell_center(pos, cell_width, cell_height, canvas_height)
        
        # Offset for multiple players in the same cell
        offset = (player_index - self.game.num_players / 2 + 0.5) * 8
        x += offset
        y += offset

        self.board_canvas.create_oval(x - 12, y - 12, x + 12, y + 12, 
                                     fill=self.player_colors[player_index], 
                                     outline="black", width=2)
        self.board_canvas.create_text(x, y, text=str(player_index + 1), 
                                     font=("Helvetica", 10, "bold"))

    def roll_dice(self):
        # Don't allow rolling during AI turn
        if self.is_ai_game and self.game.current_player == 1:
            return

        current = self.game.current_player
        dice_roll = self.game.roll_dice()

        # Update dice roll in stats
        self.player_stat_frames[current]['dice'].config(text=str(dice_roll))

        self.game.move_player(dice_roll)
        self.draw_board()
        self.update_player_stats()

        if self.game.check_win():
            self.roll_button.config(state=tk.DISABLED)
            winner_name = "AI Opponent" if (self.is_ai_game and current == 1) else f"Player {current + 1}"
            messagebox.showinfo("Winner!",
                              f"{winner_name} wins in {self.game.throws[current]} throws!")

            # Show answer frame if min_throws_bfs exists
            if hasattr(self.game, 'min_throws_bfs'):
                self.answer_frame.pack()
            else:
                self.play_again()
        else:
            self.game.next_player()
            self.update_player_stats()

            # If it's AI's turn, make it play after a delay
            if self.is_ai_game and self.game.current_player == 1:
                self.roll_button.config(state=tk.DISABLED)
                self.after(1000, self.ai_move)

    def update_player_stats(self):
        """Update all player stat displays."""
        for i in range(self.game.num_players):
            # Update status
            if i == self.game.current_player:
                self.player_stat_frames[i]['status'].config(text="Playing Now", fg="green")
                self.player_stat_frames[i]['frame'].config(relief=tk.SUNKEN, borderwidth=4)
            else:
                self.player_stat_frames[i]['status'].config(text="Waiting", fg="gray")
                self.player_stat_frames[i]['frame'].config(relief=tk.RAISED, borderwidth=3)

            # Update position
            self.player_stat_frames[i]['position'].config(text=str(self.game.player_positions[i]))

            # Update throws
            self.player_stat_frames[i]['throws'].config(text=str(self.game.throws[i]))

    def ai_move(self):
        """Make the AI opponent play automatically."""
        if self.game.current_player != 1 or not self.is_ai_game:
            return

        self.player_stat_frames[1]['status'].config(text="Thinking...", fg="orange")
        self.update()

        # AI makes a move
        dice_roll = self.game.roll_dice()
        self.player_stat_frames[1]['dice'].config(text=str(dice_roll))

        self.game.move_player(dice_roll)
        self.draw_board()
        self.update_player_stats()

        if self.game.check_win():
            self.roll_button.config(state=tk.DISABLED)
            messagebox.showinfo("Game Over",
                              f"AI Opponent wins in {self.game.throws[1]} throws!")

            if hasattr(self.game, 'min_throws_bfs'):
                self.answer_frame.pack()
            else:
                self.play_again()
        else:
            self.game.next_player()
            self.update_player_stats()
            self.roll_button.config(state=tk.NORMAL)

    def play_again(self):
        if messagebox.askyesno("Play Again?", "Do you want to play another round?"):
            self.start_game()
        else:
            self.quit()

    def check_answer(self):
        if not hasattr(self.game, 'min_throws_bfs'):
            messagebox.showerror("Error", "BFS calculation not available.")
            self.answer_frame.pack_forget()
            self.play_again()
            return
            
        try:
            guess = int(self.answer_entry.get())
            if guess == self.game.min_throws_bfs:
                messagebox.showinfo("Correct!", 
                    f"You guessed the correct minimum: {self.game.min_throws_bfs}")
                player_name = simpledialog.askstring("Player Name", 
                    f"Enter Player {self.game.current_player + 1}'s name:")
                if player_name and hasattr(self.game, 'save_result'):
                    self.game.save_result(player_name)
                    messagebox.showinfo("Saved", "Your result has been saved.")
            else:
                messagebox.showerror("Incorrect", 
                    f"Sorry, the correct answer was {self.game.min_throws_bfs}.")
        except ValueError:
            messagebox.showerror("Error", "Invalid input. Please enter a number.")
        
        self.answer_frame.pack_forget()
        self.answer_entry.delete(0, tk.END)
        self.play_again()

if __name__ == "__main__":
    app = GameGUI()
    app.mainloop()