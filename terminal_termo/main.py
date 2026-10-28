import os
import random
from terminal_ui import TerminalUI
from game_logic import GameLogic

def get_available_languages():
    languages = {}
    words_dir = 'words'
    if not os.path.exists(words_dir):
        return languages

    for filename in os.listdir(words_dir):
        if filename.startswith('words_') and filename.endswith('.txt'):
            lang_code = filename.replace('words_', '').replace('.txt', '')
            # Simple mapping for display
            display_names = {
                'en': 'English',
                'pt': 'Portuguese'
            }
            languages[display_names.get(lang_code, lang_code.upper())] = filename
    return languages

def select_language():
    languages = get_available_languages()
    if not languages:
        print("No word lists found in the 'words' directory.")
        sys.exit(1)

    print("\nChoose your language:")
    lang_list = list(languages.keys())
    for i, lang in enumerate(lang_list, 1):
        print(f"{i}. {lang}")

    while True:
        try:
            choice = int(input("\nEnter number: "))
            if 1 <= choice <= len(lang_list):
                return languages[lang_list[choice - 1]]
            else:
                print("Invalid number. Please try again.")
        except ValueError:
            print("Please enter a number.")

def load_word_list(filename):
    path = os.path.join('words', filename)
    with open(path, 'r', encoding='utf-8') as f:
        words = [line.strip().upper() for line in f if len(line.strip()) == 5]
    return words

def main():
    TerminalUI.clear_screen()
    TerminalUI.print_header()

    # 1. Game Mode Selection
    print("\nChoose Game Mode:")
    print("1. Classic (1 word, 6 tries)")
    print("2. Duo (2 words, 9 tries)")
    print("3. Quarteto (4 words, 12 tries)")

    while True:
        try:
            mode_choice = int(input("\nEnter number: "))
            if mode_choice in [1, 2, 3]:
                break
            else:
                print("Invalid choice. Please select 1, 2, or 3.")
        except ValueError:
            print("Please enter a number.")

    # 2. Language Selection
    word_file = select_language()
    word_list = load_word_list(word_file)

    if not word_list:
        print("The selected word list is empty or contains no 5-letter words.")
        return

    # Initialize game state based on mode
    if mode_choice == 1:
        targets = [random.choice(word_list)]
        max_attempts = 6
    elif mode_choice == 2:
        targets = random.sample(word_list, 2)
        max_attempts = 9
    else: # Quarteto
        targets = random.sample(word_list, 4)
        max_attempts = 12

    # Reset screen after setup for a clean game
    TerminalUI.clear_screen()
    TerminalUI.print_header()

    attempts = 0
    histories = [[] for _ in targets] # One history list per target word
    keyboard_state = {} # Track state of each letter: 'green', 'yellow', 'gray', 'none'

    while attempts < max_attempts:
        TerminalUI.clear_screen()
        TerminalUI.print_header()
        TerminalUI.display_keyboard(keyboard_state)
        TerminalUI.display_game_board(histories)

        print(f"\nAttempt {attempts + 1}/{max_attempts}")
        guess = input("Enter your guess: ").strip().upper()

        is_valid, error = GameLogic.validate_guess(guess, word_list)
        if not is_valid:
            TerminalUI.print_message(error, color='red')
            input("Press Enter to continue...")
            continue

        # Process guess against all targets
        for i, target in enumerate(targets):
            result = GameLogic.get_feedback(guess, target)
            histories[i].append((guess, result))

            # Update keyboard state based on this target
            for char, color in zip(guess, result):
                current_state = keyboard_state.get(char, 'none')
                if color == 'green':
                    keyboard_state[char] = 'green'
                elif color == 'yellow' and current_state != 'green':
                    keyboard_state[char] = 'yellow'
                elif color == 'gray' and current_state not in ['green', 'yellow']:
                    keyboard_state[char] = 'gray'

        # Check if all targets are solved
        all_solved = True
        for i, target in enumerate(targets):
            if not any(h[0] == target for h in histories[i]):
                all_solved = False
                break

        if all_solved:
            TerminalUI.clear_screen()
            TerminalUI.print_header()
            TerminalUI.display_keyboard(keyboard_state)
            TerminalUI.display_game_board(histories)
            TerminalUI.print_message(f"\nCongratulations! You discovered all words: {', '.join(targets)}!", color='green')
            break

        attempts += 1

    if attempts == max_attempts:
        TerminalUI.clear_screen()
        TerminalUI.print_header()
        TerminalUI.display_keyboard(keyboard_state)
        TerminalUI.display_game_board(histories)

        solved = [t for i, t in enumerate(targets) if any(h[0] == t for h in histories[i])]
        if len(solved) < len(targets):
            TerminalUI.print_message(f"\nGame Over! The words were: {', '.join(targets)}", color='red')

if __name__ == "__main__":
    import sys
    main()
