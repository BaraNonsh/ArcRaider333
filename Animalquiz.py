#!/usr/bin/env python3
"""
Animalquiz - A fun quiz program about animals and insects
Shows videos, asks questions, and provides feedback with sound
"""

import os
import sys

# You'll need to install these libraries:
# pip install pygame opencv-python
try:
    import pygame
    import cv2
except ImportError:
    print("Missing dependencies. Please install:")
    print("  pip install pygame opencv-python")
    sys.exit(1)


class AnimalQuiz:
    def __init__(self):
        """Initialize the quiz game"""
        pygame.mixer.init()
        self.correct_sound = None
        self.wrong_sound = None
        self.load_sounds()
        
        # Quiz data: {video_file: (question, options, answer)}
        self.quiz_data = {}
    
    def load_sounds(self):
        """Load sound files for correct and wrong answers"""
        try:
            correct_path = "sounds/correct.wav"
            wrong_path = "sounds/wrong.wav"
            
            if os.path.exists(correct_path):
                self.correct_sound = pygame.mixer.Sound(correct_path)
            if os.path.exists(wrong_path):
                self.wrong_sound = pygame.mixer.Sound(wrong_path)
        except Exception as e:
            print(f"Note: Could not load sounds - {e}")
    
    def play_video(self, video_path):
        """Display a video file"""
        if not os.path.exists(video_path):
            print(f"Error: Video file not found: {video_path}")
            return False
        
        print(f"Playing video: {video_path}")
        cap = cv2.VideoCapture(video_path)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            cv2.imshow("Animal Quiz", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        return True
    
    def ask_question(self, question, options):
        """Display a multiple choice question and get user input"""
        print("\n" + "="*50)
        print(question)
        print("="*50)
        
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        
        while True:
            try:
                choice = input("\nEnter the number of your answer: ").strip()
                choice_num = int(choice)
                if 1 <= choice_num <= len(options):
                    return options[choice_num - 1]
                else:
                    print(f"Please enter a number between 1 and {len(options)}")
            except ValueError:
                print("Invalid input. Please enter a number.")
    
    def check_answer(self, user_answer, correct_answer):
        """Check if the user's answer is correct"""
        user_answer = user_answer.strip().lower()
        correct_answer = correct_answer.strip().lower()
        
        is_correct = user_answer == correct_answer
        
        if is_correct:
            print("\nKORRIFIC!")
            if self.correct_sound:
                self.correct_sound.play()
        else:
            print("\nBUSTED!")
            print(f"The correct answer was: {correct_answer}")
            if self.wrong_sound:
                self.wrong_sound.play()
        
        return is_correct
    
    def run_quiz(self):
        """Run the main quiz loop"""
        print("\n" + "="*50)
        print("Welcome to ANIMALQUIZ!")
        print("="*50 + "\n")
        
        if not self.quiz_data:
            print("No quiz data available. Add videos to quiz_data in the code.")
            return
        
        score = 0
        total = 0
        
        for video_file, (question, options, answer) in self.quiz_data.items():
            total += 1
            
            if self.play_video(video_file):
                user_answer = self.ask_question(question, options)
                if self.check_answer(user_answer, answer):
                    score += 1
        
        print("\n" + "="*50)
        print(f"Quiz Complete! Your Score: {score}/{total}")
        print("="*50 + "\n")
    
    def add_quiz_item(self, video_path, question, options, correct_answer):
        """Add a new quiz item"""
        self.quiz_data[video_path] = (question, options, correct_answer)
        print(f"Added: {video_path}")


def main():
    """Main entry point"""
    quiz = AnimalQuiz()
    
    # Add sample quiz items
    quiz.add_quiz_item(
        "videos/lion.mp4",
        "What animal is this?",
        ["Lion", "Tiger", "Leopard"],
        "Lion"
    )
    quiz.add_quiz_item(
        "videos/bee.mp4",
        "What insect is this?",
        ["Butterfly", "Bee", "Wasp"],
        "Bee"
    )
    quiz.add_quiz_item(
        "videos/eagle.mp4",
        "What bird is this?",
        ["Hawk", "Eagle", "Falcon"],
        "Eagle"
    )
    
    quiz.run_quiz()


if __name__ == "__main__":
    main()
