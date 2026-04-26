#!/usr/bin/env python3
"""
AnimalQuiz - Main orchestrator for the interactive quiz application.

Refactored architecture with dependency injection, supporting:
- Data-driven quiz content via QuizLoader
- Decoupled multimedia handling via MultimediaController
- Clean state management and error handling
"""

from typing import Optional
import sys
import os

from quiz_loader import QuizLoader, QuizItem
from multimedia_controller import MultimediaController, MediaState


class AnimalQuiz:
    """
    Main orchestrator for the AnimalQuiz application.

    Manages quiz flow, user interaction, and score tracking using
    dependency-injected QuizLoader and MultimediaController components.
    """

    def __init__(
        self,
        quiz_loader: QuizLoader,
        multimedia_controller: MultimediaController
    ):
        """
        Initialize AnimalQuiz with injected dependencies.

        Args:
            quiz_loader (QuizLoader): Handles quiz data loading and validation.
            multimedia_controller (MultimediaController): Manages video/audio playback.

        Raises:
            ValueError: If dependencies are invalid.
        """
        if quiz_loader is None:
            raise ValueError("QuizLoader dependency cannot be None")
        if multimedia_controller is None:
            raise ValueError("MultimediaController dependency cannot be None")

        self.quiz_loader = quiz_loader
        self.multimedia_controller = multimedia_controller
        self.score = 0
        self.current_question_index = 0

    def ask_question(
        self, quiz_item: QuizItem
    ) -> Optional[str]:
        """
        Display a multiple-choice question and capture user input.

        Args:
            quiz_item (QuizItem): The quiz question to ask.

        Returns:
            Optional[str]: The user's selected option or None if input invalid.
        """
        self.multimedia_controller.current_state = MediaState.WAITING_FOR_INPUT

        print("\n" + "=" * 60)
        print(f"Question {self.current_question_index + 1}/"
              f"{self.quiz_loader.count()}")
        print("=" * 60)
        print(f"\n{quiz_item.question_text}\n")

        for i, option in enumerate(quiz_item.options, 1):
            print(f"  {i}. {option}")

        while True:
            try:
                choice = input("\nEnter the number of your answer (or 'q' to quit): ").strip()

                if choice.lower() == 'q':
                    return None

                choice_num = int(choice)
                if 1 <= choice_num <= len(quiz_item.options):
                    return quiz_item.options[choice_num - 1]
                else:
                    print(f"Please enter a number between 1 and {len(quiz_item.options)}")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def check_answer(
        self, user_answer: str, quiz_item: QuizItem
    ) -> bool:
        """
        Validate user's answer and provide feedback.

        Args:
            user_answer (str): The user's selected answer.
            quiz_item (QuizItem): The quiz item with correct answer.

        Returns:
            bool: True if answer is correct, False otherwise.
        """
        correct_answer = quiz_item.options[quiz_item.correct_index]
        is_correct = user_answer.strip().lower() == correct_answer.strip().lower()

        print("\n" + "-" * 60)

        if is_correct:
            print("✓ CORRECT!")
            self.score += 1
            self.multimedia_controller.play_feedback_audio(
                quiz_item.feedback_audio.correct
            )
        else:
            print("✗ INCORRECT!")
            print(f"The correct answer was: {correct_answer}")
            self.multimedia_controller.play_feedback_audio(
                quiz_item.feedback_audio.incorrect
            )

        print("-" * 60)
        return is_correct

    def run_quiz(self) -> None:
        """
        Execute the main quiz loop.

        Orchestrates video playback, question asking, and answer validation.
        """
        quizzes = self.quiz_loader.get_quizzes()

        if not quizzes:
            print("Error: No quizzes loaded. Cannot start quiz.")
            return

        print("\n" + "=" * 60)
        print("Welcome to ANIMALQUIZ!")
        print(f"Total Questions: {len(quizzes)}")
        print("=" * 60)

        try:
            for index, quiz_item in enumerate(quizzes):
                self.current_question_index = index

                # Play video
                if not self.multimedia_controller.play_video(quiz_item.video_path):
                    print(f"Skipping question due to video playback error")
                    continue

                # Ask question
                user_answer = self.ask_question(quiz_item)

                if user_answer is None:
                    print("\nQuiz terminated by user")
                    break

                # Check answer
                self.check_answer(user_answer, quiz_item)

                # Show current score
                print(f"Current Score: {self.score}/{index + 1}\n")

        except KeyboardInterrupt:
            print("\n\nQuiz interrupted by user")
        finally:
            self.display_results(len(quizzes))
            self.multimedia_controller.cleanup()

    def display_results(self, total_questions: int) -> None:
        """
        Display final quiz results and score.

        Args:
            total_questions (int): Total number of questions in the quiz.
        """
        percentage = (self.score / total_questions * 100) if total_questions > 0 else 0

        print("\n" + "=" * 60)
        print("QUIZ COMPLETE!")
        print("=" * 60)
        print(f"Final Score: {self.score}/{total_questions} ({percentage:.1f}%)")
        print("=" * 60 + "\n")


def initialize_resources() -> tuple:
    """
    Initialize and validate all application resources.

    Returns:
        tuple: (QuizLoader, MultimediaController) if successful.

    Raises:
        SystemExit: If critical resources are unavailable.
    """
    # Check for quiz data file
    quiz_data_path = "quiz_data.json"
    if not os.path.exists(quiz_data_path):
        print(f"Error: Quiz data file not found: {quiz_data_path}")
        sys.exit(1)

    # Load quiz data
    try:
        quiz_loader = QuizLoader(quiz_data_path)
        print(f"✓ Loaded {quiz_loader.count()} quiz items")
    except Exception as e:
        print(f"Error loading quiz data: {e}")
        sys.exit(1)

    # Initialize multimedia controller
    try:
        multimedia_controller = MultimediaController(
            display_width=1024, display_height=768
        )
        print("✓ Multimedia controller initialized")

        if not multimedia_controller.is_audio_available():
            print("⚠ Audio system unavailable (proceeding without audio)")
        else:
            print("✓ Audio system available")

    except Exception as e:
        print(f"Error initializing multimedia: {e}")
        sys.exit(1)

    return quiz_loader, multimedia_controller


def main() -> None:
    """
    Main entry point for AnimalQuiz application.

    Initializes resources and starts the quiz orchestration.
    """
    print("\n" + "=" * 60)
    print("AnimalQuiz - Initializing...")
    print("=" * 60 + "\n")

    # Initialize resources with validation
    quiz_loader, multimedia_controller = initialize_resources()

    print("\n" + "=" * 60)
    print("Starting Quiz...\n")

    # Instantiate and run quiz
    try:
        quiz = AnimalQuiz(quiz_loader, multimedia_controller)
        quiz.run_quiz()
    except Exception as e:
        print(f"Fatal error during quiz execution: {e}")
        multimedia_controller.cleanup()
        sys.exit(1)


if __name__ == "__main__":
    main()
