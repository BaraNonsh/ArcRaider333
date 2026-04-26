"""
QuizLoader Module - Handles data loading and validation for AnimalQuiz.

This module provides the QuizLoader class which is responsible for:
- Loading quiz data from JSON sources
- Validating schema compliance
- Providing typed data structures for quiz items
"""

import json
import os
from typing import List, Dict, Optional, Any
from dataclasses import dataclass


@dataclass
class FeedbackAudio:
    """Represents feedback audio paths for correct/incorrect answers."""
    correct: str
    incorrect: str

    def validate(self) -> bool:
        """Check if audio files exist."""
        return os.path.exists(self.correct) and os.path.exists(self.incorrect)


@dataclass
class QuizItem:
    """Represents a single quiz question with multimedia content."""
    id: str
    video_path: str
    question_text: str
    options: List[str]
    correct_index: int
    feedback_audio: FeedbackAudio
    difficulty: str = "medium"

    def validate(self) -> bool:
        """
        Validate quiz item integrity.

        Returns:
            bool: True if all required resources exist and structure is valid.
        """
        if not os.path.exists(self.video_path):
            print(f"Warning: Video file not found: {self.video_path}")
            return False

        if not (0 <= self.correct_index < len(self.options)):
            print(f"Error: correct_index {self.correct_index} out of range")
            return False

        if not self.feedback_audio.validate():
            print(f"Warning: Feedback audio files missing for quiz {self.id}")
            return False

        return True


class QuizLoader:
    """
    Loads and validates quiz data from JSON sources.

    This class handles I/O operations and schema validation for quiz data,
    providing a clean interface for the main AnimalQuiz orchestrator.
    """

    def __init__(self, filepath: str):
        """
        Initialize the QuizLoader with a data source filepath.

        Args:
            filepath (str): Path to the quiz_data.json file.

        Raises:
            FileNotFoundError: If the JSON file does not exist.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Quiz data file not found: {filepath}")

        self.filepath = filepath
        self._quizzes: List[QuizItem] = []
        self.load()

    def load(self) -> None:
        """
        Load and parse quiz data from JSON file.

        Raises:
            json.JSONDecodeError: If JSON is malformed.
            KeyError: If required fields are missing from schema.
        """
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            self._quizzes = self._parse_quiz_items(data.get("quizzes", []))

            if not self._quizzes:
                print("Warning: No valid quizzes loaded from file")

        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Failed to parse quiz JSON: {e.msg}",
                e.doc,
                e.pos
            )

    def _parse_quiz_items(self, quizzes_data: List[Dict[str, Any]]) -> List[QuizItem]:
        """
        Parse raw JSON data into typed QuizItem objects.

        Args:
            quizzes_data (List[Dict]): Raw quiz data from JSON.

        Returns:
            List[QuizItem]: List of validated quiz items.

        Raises:
            KeyError: If required fields are missing.
        """
        items = []

        for quiz_data in quizzes_data:
            try:
                feedback_audio = FeedbackAudio(
                    correct=quiz_data["feedback_audio"]["correct"],
                    incorrect=quiz_data["feedback_audio"]["incorrect"]
                )

                quiz_item = QuizItem(
                    id=quiz_data["id"],
                    video_path=quiz_data["video_path"],
                    question_text=quiz_data["question_text"],
                    options=quiz_data["options"],
                    correct_index=quiz_data["correct_index"],
                    feedback_audio=feedback_audio,
                    difficulty=quiz_data.get("difficulty", "medium")
                )

                if quiz_item.validate():
                    items.append(quiz_item)

            except KeyError as e:
                print(f"Warning: Skipping quiz item due to missing field: {e}")
                continue

        return items

    def get_quizzes(self) -> List[QuizItem]:
        """
        Retrieve all loaded quiz items.

        Returns:
            List[QuizItem]: List of quiz items.
        """
        return self._quizzes

    def get_quiz_by_id(self, quiz_id: str) -> Optional[QuizItem]:
        """
        Retrieve a specific quiz by ID.

        Args:
            quiz_id (str): The unique quiz identifier.

        Returns:
            Optional[QuizItem]: The quiz item if found, None otherwise.
        """
        for quiz in self._quizzes:
            if quiz.id == quiz_id:
                return quiz
        return None

    def count(self) -> int:
        """
        Get the total number of loaded quizzes.

        Returns:
            int: Total quiz count.
        """
        return len(self._quizzes)
