import random

class GameLogic:
    @staticmethod
    def get_feedback(guess, target):
        """
        Compares guess with target and returns a list of colors.
        green: correct letter, correct position
        yellow: correct letter, wrong position
        gray: letter not in target
        """
        guess = guess.upper()
        target = target.upper()
        result = ['gray'] * 5

        # First pass: Find green (correct positions)
        target_remaining = list(target)
        guess_remaining = list(guess)

        for i in range(5):
            if guess[i] == target[i]:
                result[i] = 'green'
                target_remaining[i] = None
                guess_remaining[i] = None

        # Second pass: Find yellow (wrong positions)
        for i in range(5):
            if guess_remaining[i] is not None:
                char = guess_remaining[i]
                if char in target_remaining:
                    result[i] = 'yellow'
                    # Remove only one instance of the letter from remaining target
                    target_remaining[target_remaining.index(char)] = None

        return result

    @staticmethod
    def validate_guess(guess, word_list):
        """
        Returns (is_valid, error_message)
        """
        if len(guess) != 5:
            return False, "The word must be exactly 5 letters long."

        if guess.upper() not in word_list:
            return False, "The word is not in the word list."

        return True, None
