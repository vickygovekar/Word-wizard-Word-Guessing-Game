import tkinter as tk
from tkinter import messagebox, ttk
import random
import threading
import time
from collections import deque
from fuzzywuzzy import fuzz
import csv
from PIL import Image, ImageTk  # For image handling
import os
import re  # For regex pattern matching in hints

# --- BFS File-Based Word Picker ---
class FileBFS:
    def __init__(self, filepath='words.csv'):
        self.graph = {}
        with open(filepath, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                word = row['word'].strip().lower()
                hint = row['hint'].strip()
                neighbors = [w.strip().lower() for w in row['neighbors'].split(';') if w.strip()]
                self.graph[word] = {'hint': hint, 'neighbors': neighbors}

    def get_word(self, start, max_depth=1, min_len=4, max_len=10):
        visited = set()
        queue = deque([(start.lower(), 0)])
        candidates = []
        while queue:
            node, depth = queue.popleft()
            if node in visited:
                continue
            visited.add(node)
            if node in self.graph:
                if min_len <= len(node) <= max_len and node.isalpha():
                    candidates.append((node, depth))
                if depth < max_depth:
                    for nbr in self.graph[node]['neighbors']:
                        if nbr not in visited:
                            queue.append((nbr, depth + 1))
        if not candidates:
            return None
        max_found = max(d for _, d in candidates) if candidates else 0
        top = [w for w, d in candidates if d == max_found]
        return random.choice(top) if top else None

    def get_hint(self, word):
        word = word.lower()
        if word in self.graph and self.graph[word]['hint']:
            # Return the hint but make sure it doesn't contain the actual word
            hint = self.graph[word]['hint']
            # Replace the actual word or any form of it with "it" or "this word"
            # Case-insensitive replacement
            hint_lower = hint.lower()
            word_lower = word.lower()
            
            if word_lower in hint_lower:
                replacements = ["this word", "it", "this term", "the answer"]
                replacement = random.choice(replacements)
                # Find all occurrences of the word in the hint
                hint = re.sub(r'\b' + re.escape(word_lower) + r'\b', replacement, hint_lower, flags=re.IGNORECASE)
                hint = hint[0].upper() + hint[1:]  # Capitalize first letter
                
            return hint
        return "Think about this word carefully."

# --- Game Animation Effects ---
class AnimationEffects:
    @staticmethod
    def fade_in(widget, duration=500, steps=20):
        """Gradually fade in a widget"""
        widget.place_forget() if hasattr(widget, 'place_forget') else widget.pack_forget()
        widget.update()
        
        # Make sure it's visible at 0 opacity first
        if hasattr(widget, 'place'):
            widget.place(relx=0.5, rely=0.5, anchor='center')
        else:
            widget.pack()
            
        for i in range(steps + 1):
            opacity = i / steps
            widget.configure(style=f"{widget.cget('style').split('.')[0]}.{opacity}.TLabel")
            widget.update()
            time.sleep(duration / 1000 / steps)
    
    @staticmethod
    def highlight_widget(widget, color='#FFD700', duration=300):
        """Briefly highlight a widget"""
        original_bg = widget.cget('background')
        widget.configure(background=color)
        widget.update()
        widget.after(duration, lambda: widget.configure(background=original_bg))
    
    @staticmethod
    def shake_widget(widget, distance=10, cycles=5, duration=50):
        """Shake a widget left and right"""
        original_x = widget.winfo_x()
        for i in range(cycles):
            widget.place(x=original_x + distance)
            widget.update()
            time.sleep(duration / 1000)
            widget.place(x=original_x - distance)
            widget.update()
            time.sleep(duration / 1000)
        widget.place(x=original_x)

# --- Game Logic & Enhanced UI ---
class WordGuessingGame:
    def __init__(self, master, word_file='words.csv'):
        self.master = master
        self.master.title("🧠 Word Wizard: AI Guessing Game 🧠")
        self.master.configure(bg="#1e1e2e")
        self.master.geometry("900x700")
        self.master.resizable(False, False)  # Fixed window size for consistent UI
        
        # Add window icon if available
        try:
            self.master.iconbitmap("word_game_icon.ico")
        except:
            pass
            
        self.datasource = FileBFS(word_file)
        self.style = ttk.Style()
        self._setup_styles()
        self._load_assets()
        self._init_game_state()
        self.setup_start_menu()
        
        # Add keyboard events
        self.master.bind('<Escape>', lambda e: self.exit_prompt())

    def _load_assets(self):
        """Load images and other assets"""
        self.images = {}
        # Create a simple logo if no image available
        self.images['logo'] = self._create_text_image("WORD WIZARD", (300, 120), "#f9d949", "#1e1e2e", 42)
        
        # Create difficulty badges
        self.images['easy'] = self._create_text_image("EASY", (100, 40), "#4CAF50", "#ffffff", 16)
        self.images['medium'] = self._create_text_image("MEDIUM", (100, 40), "#FF9800", "#ffffff", 16)
        self.images['hard'] = self._create_text_image("HARD", (100, 40), "#F44336", "#ffffff", 16)
        
        # Sound effects (we'll just prepare placeholders but not implement actual sounds)
        self.sounds = {
            'correct': None,
            'wrong': None,
            'click': None,
            'win': None,
            'lose': None,
        }

    def _create_text_image(self, text, size, bg_color, text_color, font_size):
        """Create a simple image with text for buttons/logos"""
        img = Image.new('RGBA', size, bg_color)
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        # Use default font if custom font not available
        try:
            font = ImageFont.truetype("Arial Bold", font_size)
        except:
            font = ImageFont.load_default()
        
        # Center text
        text_width, text_height = draw.textsize(text, font=font) if hasattr(draw, 'textsize') else (size[0]-20, size[1]-10)
        position = ((size[0]-text_width)/2, (size[1]-text_height)/2)
        draw.text(position, text, fill=text_color, font=font)
        
        return ImageTk.PhotoImage(img)

    def _setup_styles(self):
        # Overall theme
        self.style.theme_use('clam')

        # Color palette - Cyberpunk/Tech theme
        colors = {
            'bg_dark': '#1e1e2e',      # Dark background
            'bg_light': '#2d2d44',     # Light background
            'accent1': '#f9d949',      # Yellow accent
            'accent2': '#7e52a0',      # Purple accent  
            'text_light': '#ffffff',   # Light text
            'text_dark': '#dcdcdc',    # Dark text
            'success': '#50fa7b',      # Success green
            'error': '#ff5555',        # Error red
            'warning': '#f1fa8c',      # Warning yellow
            'info': '#8be9fd',         # Info blue
        }
        
        # Frame styles
        self.style.configure('Game.TFrame', background=colors['bg_dark'])
        
        # Label styles
        for style_name, config in {
            'Title.TLabel': {'font': ('Verdana', 32, 'bold'), 'foreground': colors['accent1'], 'background': colors['bg_dark']},
            'Subtitle.TLabel': {'font': ('Verdana', 16), 'foreground': colors['text_light'], 'background': colors['bg_dark']},
            'Header.TLabel': {'font': ('Verdana', 24, 'bold'), 'foreground': colors['accent1'], 'background': colors['bg_dark']},
            'Info.TLabel': {'font': ('Verdana', 14), 'foreground': colors['text_light'], 'background': colors['bg_light']},
            'Word.TLabel': {'font': ('Courier New', 40, 'bold'), 'foreground': colors['accent1'], 'background': colors['bg_dark']},
            'Timer.TLabel': {'font': ('Verdana', 18, 'bold'), 'foreground': colors['warning'], 'background': colors['bg_dark']},
            'Score.TLabel': {'font': ('Verdana', 16, 'bold'), 'foreground': colors['accent1'], 'background': colors['bg_dark']},
            'Feedback.Success.TLabel': {'font': ('Verdana', 16, 'bold'), 'foreground': colors['success'], 'background': colors['bg_dark']},
            'Feedback.Error.TLabel': {'font': ('Verdana', 16, 'bold'), 'foreground': colors['error'], 'background': colors['bg_dark']},
            'Feedback.Info.TLabel': {'font': ('Verdana', 14), 'foreground': colors['info'], 'background': colors['bg_dark']},
        }.items():
            self.style.configure(style_name, **config)
            
        # Button styles
        for style_name, config in {
            'Primary.TButton': {
                'font': ('Verdana', 14, 'bold'), 
                'background': colors['accent2'],
                'foreground': colors['text_light']
            },
            'Secondary.TButton': {
                'font': ('Verdana', 12), 
                'background': colors['bg_light'],
                'foreground': colors['text_light']
            },
            'Success.TButton': {
                'font': ('Verdana', 14, 'bold'), 
                'background': colors['success'],
                'foreground': colors['bg_dark']
            },
            'Danger.TButton': {
                'font': ('Verdana', 14, 'bold'), 
                'background': colors['error'],
                'foreground': colors['text_light']
            },
        }.items():
            self.style.configure(style_name, **config)
            # Add hover effect mapping
            hover_bg = self._lighten_color(config['background'], 0.2)
            self.style.map(style_name, 
                background=[('active', hover_bg), ('pressed', config['background'])],
                relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
        
        # Entry style
        self.style.configure('Game.TEntry', 
                            font=('Verdana', 16),
                            fieldbackground=colors['bg_light'],
                            foreground=colors['text_light'])
        
        # Progressbar style
        self.style.configure('Game.Horizontal.TProgressbar',
                            background=colors['accent1'],
                            troughcolor=colors['bg_light'])
    
    def _lighten_color(self, hex_color, factor=0.1):
        """Lighten a hex color by a factor"""
        # Convert hex to RGB
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Lighten
        new_rgb = tuple(min(255, int(c + (255 - c) * factor)) for c in rgb)
        
        # Convert back to hex
        return f'#{new_rgb[0]:02x}{new_rgb[1]:02x}{new_rgb[2]:02x}'

    def _init_game_state(self):
        self.difficulty = None
        self.word = None
        self.hint = None
        self.display_word = None
        # total lifelines across the entire game
        self.total_lifelines = 10
# only one lifeline available per question
        self.lifelines = 1
        self.correct_streak = 0
        self.wrong_streak = 0
        self.timer_seconds = 30
        self.timer_id = None
        self.total_questions = 10
        self.current_question = 0
        self.score = 0
        self.used_words = set()
        self.animations = AnimationEffects()

    def clear_widgets(self):
        for widget in self.master.winfo_children():
            widget.destroy()

    def setup_start_menu(self):
        self.clear_widgets()
        
        # Container frame with background
        main_frame = ttk.Frame(self.master, style='Game.TFrame')
        main_frame.pack(fill='both', expand=True)
        
        # Title with logo
        logo_label = ttk.Label(main_frame, image=self.images['logo'])
        logo_label.pack(pady=(80, 20))
        
        subtitle = ttk.Label(main_frame, text="Challenge your vocabulary with AI", style='Subtitle.TLabel')
        subtitle.pack(pady=(0, 60))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame, style='Game.TFrame')
        button_frame.pack()
        
        # Start button with 3D effect
        start_btn = ttk.Button(
            button_frame, 
            text="Start Game", 
            style='Primary.TButton',
            command=self.setup_difficulty_menu
        )
        start_btn.pack(ipadx=30, ipady=15, pady=10)
        
        # Additional buttons
        how_to_btn = ttk.Button(
            button_frame, 
            text="How to Play", 
            style='Secondary.TButton',
            command=self.show_instructions
        )
        how_to_btn.pack(ipadx=20, ipady=10, pady=10)
        
        exit_btn = ttk.Button(
            button_frame, 
            text="Exit", 
            style='Danger.TButton',
            command=self.exit_prompt
        )
        exit_btn.pack(ipadx=20, ipady=10, pady=(10, 0))
        
        # Version info
        version_label = ttk.Label(
            main_frame, 
            text="v1.0", 
            style='Subtitle.TLabel'
        )
        version_label.pack(side='bottom', pady=10)

    def show_instructions(self):
        """Show game instructions in a popup"""
        instructions = tk.Toplevel(self.master)
        instructions.title("How to Play")
        instructions.geometry("500x400")
        instructions.configure(bg="#1e1e2e")
        instructions.transient(self.master)
        instructions.grab_set()
        
        # Add instructions content
        frame = ttk.Frame(instructions, style='Game.TFrame')
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(frame, text="How to Play", style='Header.TLabel').pack(pady=10)
        
        instructions_text = """
1. Choose your difficulty level: Easy, Medium, or Hard
2. You'll be given a word with letters hidden
3. Read the hint provided and try to guess the word
4. Type your guess and submit before the timer runs out
5. Use the 'Hint Reveal' lifeline to reveal a letter when stuck
6. Get points for correct answers
7. Complete all 10 words to finish the game
        """
        
        ttk.Label(frame, text=instructions_text, style='Info.TLabel', wraplength=400).pack(pady=20)
        
        ttk.Button(frame, text="Close", style='Secondary.TButton', 
                   command=instructions.destroy).pack(pady=10)

    def exit_prompt(self):
        """Confirm before exiting"""
        if messagebox.askyesno("Exit Game", "Are you sure you want to exit the game?"):
            self.master.quit()

    def setup_difficulty_menu(self):
        self.clear_widgets()
        
        # Main frame
        main_frame = ttk.Frame(self.master, style='Game.TFrame')
        main_frame.pack(fill='both', expand=True)
        
        # Title
        ttk.Label(main_frame, text="Select Difficulty", style='Header.TLabel').pack(pady=40)
        
        # Difficulty buttons with images and descriptions
        difficulties = [
            ("Easy", "Perfect for beginners\nMore time, simpler words", self.images['easy']),
            ("Medium", "Balanced challenge\nModerate time, varied words", self.images['medium']),
            ("Hard", "For word experts\nLess time, complex words", self.images['hard'])
        ]
        
        button_frame = ttk.Frame(main_frame, style='Game.TFrame')
        button_frame.pack(pady=20)
        
        for diff, desc, img in difficulties:
            diff_frame = ttk.Frame(button_frame, style='Game.TFrame')
            diff_frame.pack(side='left', padx=20, pady=10)
            
            # Badge/image
            ttk.Label(diff_frame, image=img).pack(pady=5)
            
            # Button
            btn = ttk.Button(
                diff_frame, text=diff, style='Primary.TButton', width=12,
                command=lambda d=diff: self.start_game(d)
            )
            btn.pack(pady=5)
            
            # Description
            ttk.Label(diff_frame, text=desc, style='Info.TLabel', wraplength=150).pack(pady=5)
        
        # Back button
        ttk.Button(main_frame, text="← Back", style='Secondary.TButton', 
                  command=self.setup_start_menu).pack(pady=30)

    def start_game(self, difficulty):
        self._init_game_state()
        self.difficulty = difficulty
        self.lifelines = {"Easy": 2, "Medium": 1, "Hard": 1}[difficulty]
        self.clear_widgets()
        self.setup_game_widgets()
        self.next_word()

    def setup_game_widgets(self):
        # Main container
        self.game_frame = ttk.Frame(self.master, style='Game.TFrame')
        self.game_frame.pack(fill='both', expand=True)
        
        # Header with game info
        header_frame = ttk.Frame(self.game_frame, style='Game.TFrame')
        header_frame.pack(fill='x', padx=20, pady=10)
        
        # Left side: Difficulty badge
        left_frame = ttk.Frame(header_frame, style='Game.TFrame')
        left_frame.pack(side='left')
        diff_img = self.images[self.difficulty.lower()]
        ttk.Label(left_frame, image=diff_img).pack(side='left', padx=5)
        
        # Center: Progress info
        center_frame = ttk.Frame(header_frame, style='Game.TFrame')
        center_frame.pack(side='left', expand=True, padx=50)
        
        self.question_counter = ttk.Label(
            center_frame, 
            text=f"Word 1/{self.total_questions}", 
            style='Info.TLabel'
        )
        self.question_counter.pack(pady=5)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            center_frame, 
            orient='horizontal', 
            length=300, 
            mode='determinate',
            style='Game.Horizontal.TProgressbar'
        )
        self.progress_bar.pack(fill='x', pady=5)
        
        # Right side: Score
        right_frame = ttk.Frame(header_frame, style='Game.TFrame')
        right_frame.pack(side='right')
        
        self.score_label = ttk.Label(
            right_frame, 
            text=f"Score: {self.score}", 
            style='Score.TLabel'
        )
        self.score_label.pack(padx=5)
        
        # Game area
        game_area = ttk.Frame(self.game_frame, style='Game.TFrame')
        game_area.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Hint section
        hint_frame = ttk.Frame(game_area, style='Game.TFrame')
        hint_frame.pack(fill='x', pady=10)
        
        ttk.Label(hint_frame, text="HINT:", style='Info.TLabel').pack(anchor='w')
        self.hint_label = ttk.Label(
            hint_frame, 
            text="Loading...", 
            style='Info.TLabel', 
            wraplength=800
        )
        self.hint_label.pack(fill='x', pady=5)
        
        # Word display
        word_frame = ttk.Frame(game_area, style='Game.TFrame')
        word_frame.pack(fill='x', pady=20)
        
        self.word_label = ttk.Label(word_frame, text="", style='Word.TLabel')
        self.word_label.pack(pady=10)
        
        # Timer
        timer_frame = ttk.Frame(game_area, style='Game.TFrame')
        timer_frame.pack(fill='x')
        
        self.timer_label = ttk.Label(timer_frame, text="Time: 30s", style='Timer.TLabel')
        self.timer_label.pack()
        
        # Input area
        input_frame = ttk.Frame(game_area, style='Game.TFrame')
        input_frame.pack(fill='x', pady=20)
        
        # Entry with styling
        self.entry = ttk.Entry(input_frame, font=('Verdana', 18), width=25, justify='center')
        self.entry.pack(side='left', padx=10, ipady=5, expand=True)
        self.entry.bind('<Return>', lambda e: self.check_answer())
        self.entry.focus_set()  # Auto-focus on entry
        
        # Submit button
        self.submit_btn = ttk.Button(
            input_frame, 
            text="Submit Answer", 
            style='Success.TButton',
            command=self.check_answer
        )
        self.submit_btn.pack(side='left', padx=10, ipadx=10, ipady=5)
        
        # Controls frame
        controls_frame = ttk.Frame(game_area, style='Game.TFrame')
        controls_frame.pack(fill='x', pady=10)
        
        # Lifeline button
        self.lifeline_btn = ttk.Button(
            controls_frame, 
            text=f"Reveal Letter ({self.lifelines})", 
            style='Primary.TButton',
            command=self.use_lifeline
        )
        self.lifeline_btn.pack(side='left', padx=10, ipadx=10, ipady=5)
        
        # Next word button
        self.next_btn = ttk.Button(
            controls_frame, 
            text="Next Word →", 
            style='Secondary.TButton',
            command=self.next_word
        )
        self.next_btn.pack(side='right', padx=10, ipadx=10, ipady=5)
        
        # Feedback area
        feedback_frame = ttk.Frame(game_area, style='Game.TFrame')
        feedback_frame.pack(fill='x', pady=10)
        
        self.feedback_label = ttk.Label(feedback_frame, text="", style='Feedback.Info.TLabel')
        self.feedback_label.pack(pady=5)
        
        # Home button at bottom
        home_frame = ttk.Frame(self.game_frame, style='Game.TFrame')
        home_frame.pack(side='bottom', fill='x', pady=10)
        
        ttk.Button(
            home_frame, 
            text="◀ Menu", 
            style='Secondary.TButton',
            command=lambda: self.confirm_exit_game()
        ).pack(side='left', padx=20)

    def confirm_exit_game(self):
        """Ask before returning to main menu"""
        if messagebox.askyesno("Exit Game", "Are you sure you want to return to the main menu?\nYour progress will be lost."):
            self.setup_start_menu()

    def next_word(self):
        if self.current_question >= self.total_questions:
            return self.end_game()
        
        # Clean up previous timer if exists
        if self.timer_id:
            self.master.after_cancel(self.timer_id)
            self.timer_id = None
            
        self.current_question += 1
        self.question_counter.config(text=f"Word {self.current_question}/{self.total_questions}")
        self.progress_bar['value'] = (self.current_question - 1) / self.total_questions * 100
        
        # Reset UI elements
        self.entry.delete(0, tk.END)
        self.entry.config(state='normal')  # Re-enable entry for next word
        self.submit_btn.config(state='normal')  # Re-enable submit button
        self.feedback_label.config(text="")
        self.hint_label.config(text="Loading new word...")
        self.word_label.config(text="")
        self.master.update()

        # Update difficulty settings
        max_depth = {"Easy": 1, "Medium": 2, "Hard": 3}[self.difficulty]
        seeds = list(self.datasource.graph.keys())
        random.shuffle(seeds)

        def load():
            sel = None
            for _ in range(20):
                seed = random.choice(seeds)
                w = self.datasource.get_word(seed, max_depth=max_depth)
                if w and w not in self.used_words:
                    sel = (w, self.datasource.get_hint(w))
                    break
            if not sel:
                sel = ('orange', 'A citrus fruit known for its vitamin C.')
            self.master.after(0, lambda: self.set_word_and_hint(*sel))

        threading.Thread(target=load, daemon=True).start()

    def set_word_and_hint(self, word, hint):
        self.word = word
        self.hint = hint
        self.used_words.add(word)
        
        # Create masked word display
        self.display_word = ['_' if c.isalpha() else c for c in word]

        # --- auto-reveal 2 letters at start of each question ---
        hidden_indices = [i for i, ch in enumerate(self.display_word) if ch == '_']
        random.shuffle(hidden_indices)
        for idx in hidden_indices[:2]:
            self.display_word[idx] = self.word[idx]
        # ---------------------------------------------------------

        # Add some animation effects for new word appearance
        self.hint_label.config(text=hint)
        
        # Show word with nice spacing
        self.word_label.config(text=" ".join(self.display_word))
        
        # reset per-question lifeline from remaining pool
        self.lifelines = 1 if self.total_lifelines > 0 else 0
        self.lifeline_btn.config(
            text=f"Reveal Letter ({self.lifelines})",
            state='normal' if self.lifelines else 'disabled'
        )
        
        # Start timer with appropriate time based on difficulty
        self.start_timer()

    def start_timer(self):
        self.timer_seconds = {"Easy": 30, "Medium": 25, "Hard": 20}[self.difficulty]
        self._countdown()

    def _countdown(self):
        # Update timer display with color changes as time runs low
        if self.timer_seconds <= 5:
            self.timer_label.config(text=f"⏰ Time: {self.timer_seconds}s", foreground='#ff5555')
        else:
            self.timer_label.config(text=f"Time: {self.timer_seconds}s")
            
        if self.timer_seconds > 0:
            self.timer_seconds -= 1
            self.timer_id = self.master.after(1000, self._countdown)
        else:
            # Time's up!
            self.feedback_label.config(
                text=f"⏰ Time's up! The word was: {self.word}", 
                style='Feedback.Error.TLabel'
            )
            # Disable entry and submit
            self.entry.config(state='disabled')
            self.submit_btn.config(state='disabled')

    def check_answer(self):
        guess = self.entry.get().strip().lower()
        if not guess:
            self.feedback_label.config(
                text="Please enter a guess!", 
                style='Feedback.Info.TLabel'
            )
            return
            
        # Stop the timer
        if self.timer_id:
            self.master.after_cancel(self.timer_id)
            self.timer_id = None
            
        # Check answer using fuzzy matching
        sc = fuzz.ratio(guess, self.word)
        
        if sc >= 80:  # Close enough match
            # Correct answer!
            self.score += max(5, self.timer_seconds // 2)  # Bonus points for speed
            self.score_label.config(text=f"Score: {self.score}")
            
            # Show success feedback with animation
            self.feedback_label.config(
                text=f"✅ Correct! '{self.word}' was the answer!", 
                style='Feedback.Success.TLabel'
            )
            
            # Reveal the word
            self.word_label.config(text=" ".join(self.word))
            
            # Disable input until next word
            self.entry.config(state='disabled')
            self.submit_btn.config(state='disabled')
            
            # Auto-proceed to next word after delay
            self.master.after(2000, self.next_word)
        else:
            # Wrong answer
            self.feedback_label.config(
                text=f"❌ Incorrect! The word was: {self.word}", 
                style='Feedback.Error.TLabel'
            )
            
            # Reveal the word
            self.word_label.config(text=" ".join(self.word))
            
            # Disable input until next word
            self.entry.config(state='disabled')
            self.submit_btn.config(state='disabled')

    def use_lifeline(self):
        # only allow if overall pool and this question both have lifelines
        if self.total_lifelines <= 0 or self.lifelines <= 0:
            return

        # Find a hidden letter to reveal
        hidden_indices = [i for i, letter in enumerate(self.display_word) if letter == '_']

        if hidden_indices:
            # Choose a random hidden letter to reveal
            idx = random.choice(hidden_indices)
            self.display_word[idx] = self.word[idx]

            # Update the display
            self.word_label.config(text=" ".join(self.display_word))

            # consume one from the overall pool and disable for this question
            self.total_lifelines -= 1
            self.lifelines = 0
            self.lifeline_btn.config(
                text=f"Reveal Letter ({self.lifelines})",
                state='disabled'
            )


    def end_game(self):
        """Show game over screen with stats"""
        self.clear_widgets()
        
        # Container frame
        end_frame = ttk.Frame(self.master, style='Game.TFrame')
        end_frame.pack(fill='both', expand=True)
        
        # Game over banner
        ttk.Label(end_frame, text="Game Complete!", style='Header.TLabel').pack(pady=(80, 20))
        
        # Score display with animation effect
        score_display = ttk.Label(
            end_frame, 
            text=f"Final Score: {self.score}/{self.total_questions*10}", 
            style='Title.TLabel'
        )
        score_display.pack(pady=20)
        
        # Performance message
        performance_text = "Great job!" if self.score > self.total_questions*5 else " skill issue Keep practicing!"
        ttk.Label(end_frame, text=performance_text, style='Subtitle.TLabel').pack(pady=10)
        
        # Stats section
        stats_frame = ttk.Frame(end_frame, style='Game.TFrame')
        stats_frame.pack(pady=30)
        
        ttk.Label(stats_frame, text=f"Difficulty: {self.difficulty}", style='Info.TLabel').pack(pady=5)
        ttk.Label(stats_frame, text=f"Words Played: {self.total_questions}", style='Info.TLabel').pack(pady=5)
        
        # Buttons
        button_frame = ttk.Frame(end_frame, style='Game.TFrame')
        button_frame.pack(pady=40)
        
        ttk.Button(
            button_frame, 
            text="Play Again", 
            style='Primary.TButton',
            command=self.setup_difficulty_menu
        ).pack(side='left', padx=10, ipadx=10, ipady=5)
        
        ttk.Button(
            button_frame, 
            text="Main Menu", 
            style='Secondary.TButton',
            command=self.setup_start_menu
        ).pack(side='left', padx=10, ipadx=10, ipady=5)
        
        ttk.Button(
            button_frame, 
            text="Exit Game", 
            style='Danger.TButton',
            command=self.exit_prompt
        ).pack(side='left', padx=10, ipadx=10, ipady=5)

# --- Run ---
if __name__ == '__main__':
    root = tk.Tk()
    app = WordGuessingGame(root, word_file='words.csv')
    root.mainloop()