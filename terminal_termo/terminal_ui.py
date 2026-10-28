import sys

class TerminalUI:
    # ANSI Color Codes
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    GRAY = '\033[90m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'


    @staticmethod
    def print_header():
        print(f"\n{TerminalUI.BOLD}=== TERMINAL TERMO ==={TerminalUI.RESET}")
        print("Guess the 5-letter word!\n")

    @staticmethod
    def display_game_board(histories, current_guess=None):
        """
        histories: list of lists, each inner list is for one target word
        each history is a list of tuples (guess, result)
        """
        print("\n")
        # Determine max attempts based on the first history's intended limit
        # In Duo mode we might have more, but we'll handle it dynamically
        max_attempts = 6 if len(histories) == 1 else 9

        # To display side-by-side, we iterate by attempt index
        for i in range(max_attempts):
            row_output = ""
            for h in histories:
                if i < len(h):
                    guess, result = h[i]
                    word_output = ""
                    for char, color in zip(guess, result):
                        if color == 'green':
                            c = TerminalUI.GREEN
                        elif color == 'yellow':
                            c = TerminalUI.YELLOW
                        else:
                            c = TerminalUI.GRAY
                        word_output += f"{c}[{char}]{TerminalUI.RESET} "
                    row_output += word_output + "    " # Space between words
                else:
                    row_output += "[ ] [ ] [ ] [ ] [ ]    "
            print(row_output)
        print("")


    @staticmethod
    def display_keyboard(keyboard_state):
        """
        keyboard_state: dict where key is character and value is color ('green', 'yellow', 'gray', 'none')
        """
        rows = [
            "QWERTYUIOP",
            "ASDFGHJKL",
            "ZXCVBNM"
        ]

        print("\nKeyboard:")
        for row in rows:
            line = " "
            for char in row:
                state = keyboard_state.get(char, 'none')
                if state == 'green':
                    c = TerminalUI.GREEN
                elif state == 'yellow':
                    c = TerminalUI.YELLOW
                elif state == 'gray':
                    c = TerminalUI.GRAY
                else:
                    c = TerminalUI.RESET

                # Using DIM for letters not yet used
                if state == 'none':
                    line += f"{TerminalUI.DIM}{c}{char}{TerminalUI.RESET} "
                else:
                    line += f"{c}{char}{TerminalUI.RESET} "
            print(line)
        print("")


    @staticmethod
    def print_message(message, color=None):
        if color == 'red':
            print(f"\033[91m{message}\033[0m")
        elif color == 'green':
            print(f"\033[92m{message}\033[0m")
        else:
            print(message)

    @staticmethod
    def clear_screen():
        # Clear terminal screen
        print("\033[H\033[J", end="")
