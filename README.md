# Word Wizard: AI-Powered Word Guessing Game


## 📖 Introduction

**Word Wizard** is an engaging, desktop-based word guessing game built in **Python** using **Tkinter**. It tests and enhances your vocabulary by presenting masked words and smart hints. With AI-inspired word selection, lifelines, and fuzzy logic for answer validation, the game offers an educational and entertaining experience.

---

## ✨ Features

* 🎯 **AI-Powered Word Selection**: Uses BFS on a word graph for contextual word choices.
* 💡 **Smart Hints**: Automatically masks the actual answer in hints using regex.
* ⏱️ **Timer Challenge**: Time limits vary by difficulty (Easy, Medium, Hard).
* 🧩 **Lifelines**: Reveal one letter per round to assist when stuck.
* 🤖 **Fuzzy Answer Checking**: Allows minor spelling mistakes with fuzzy matching.
* 💾 **Game State Saving**: Save and load progress using JSON files.
* 📊 **Player Stats**: Tracks wins, losses, streaks, and average time.
* 🎨 **Dynamic UI & Animations**: Smooth fade-ins, highlights, and shake effects enhance the user experience.

---

## 🛠️ Getting Started

### Prerequisites

Make sure you have the following installed:

* Python 3.7 or higher
* `tkinter` (usually bundled with Python)
* `pillow` for image handling
* `fuzzywuzzy` for fuzzy word matching

Install required packages:

```bash
pip install pillow fuzzywuzzy
```

### Installation

1. Clone this repository:

```bash
git clone https://github.com/vickygovekar/word-wizard-word-guessing-game.git
cd word-wizard-word-guessing-game
```

2. Ensure a `words.csv` file exists in the root directory with the following columns:

   * `word`, `hint`, `neighbors`, (optional: `category`)

### Running the Game

```bash
python pygame2.py
```

---

## 📦 Usage

* Launch the game and select a difficulty level.
* Guess the word using the given hint before the timer runs out.
* Use lifelines to reveal a letter if you're stuck.
* Answer 10 questions to complete the game.
* Save/load your progress anytime.

---

## 🗂️ Project Structure

```
word-wizard/
├── pygame2.py             # Main application code
├── words.csv              # Word database file
├── game_state.json        # JSON file for saving game state
├── word_game_icon.ico     # Optional icon for the game window
├── screenshots/           # Folder for game screenshots
├── LICENSE
└── README.md
```

---

## 🤝 Contributing

Contributions are welcome! 🛠️

To contribute:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your message'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a pull request

Feel free to open an issue for bug reports or suggestions.
