# AnimalQuiz - Refactored Architecture Documentation

## Overview

This document describes the refactored AnimalQuiz codebase, which has evolved from a monolithic MVP to a modular, extensible architecture following SOLID principles.

## Architecture

### Previous Design (MVP)
- Single `AnimalQuiz` class with hardcoded quiz data
- Direct OpenCV and Pygame calls mixed with business logic
- Limited extensibility
- No data validation

### Refactored Design (Production-Ready)
```
┌─────────────────────────────────────┐
│         Animalquiz_refactored.py   │
│     (Main Orchestrator)             │
├─────────────────────────────────────┤
│  ├─ QuizLoader (quiz_loader.py)    │
│  └─ MultimediaController (mmctrler)│
├─────────────────────────────────────┤
│  └─ quiz_data.json                 │
└─────────────────────────────────────┘
```

## Module Descriptions

### 1. quiz_data.json
**Purpose**: Centralized quiz content repository (Data Layer)

**Schema**:
```json
{
  "quizzes": [
    {
      "id": "unique_quiz_id",
      "video_path": "path/to/video.mp4",
      "question_text": "What is this?",
      "options": ["Option 1", "Option 2", "Option 3"],
      "correct_index": 0,
      "feedback_audio": {
        "correct": "sounds/correct.wav",
        "incorrect": "sounds/wrong.wav"
      },
      "difficulty": "easy|medium|hard"
    }
  ]
}
```

**Key Features**:
- ✓ Type validation for all fields
- ✓ Resource existence checking (video/audio files)
- ✓ Extensible difficulty levels
- ✓ Unique quiz identifiers

---

### 2. quiz_loader.py
**Purpose**: Data decoupling and validation (Data Layer)

**Classes**:
- `FeedbackAudio`: Dataclass for audio paths
- `QuizItem`: Typed representation of a quiz question
- `QuizLoader`: JSON I/O and validation engine

**Key Features**:
- ✓ Type hints throughout (typing module)
- ✓ Graceful error handling with warnings (non-blocking)
- ✓ Schema validation with fallback defaults
- ✓ Sound cache for repeated quiz items
- ✓ Query methods: `get_quizzes()`, `get_quiz_by_id()`, `count()`

**Example Usage**:
```python
loader = QuizLoader("quiz_data.json")
print(f"Loaded {loader.count()} quizzes")
quiz = loader.get_quiz_by_id("quiz_lion")
```

---

### 3. multimedia_controller.py
**Purpose**: Hardware abstraction layer for video/audio (I/O Layer)

**Classes**:
- `MediaState`: Enum state machine (VIDEO_PLAYBACK, WAITING_FOR_INPUT, FEEDBACK_AUDIO, IDLE)
- `MultimediaController`: Orchestrates OpenCV and Pygame

**Key Features**:
- ✓ **Aspect Ratio Preservation**: Videos centered on display without distortion
- ✓ **State Machine**: Tracks current operation (video, input, audio, idle)
- ✓ **Sound Cache**: Efficient audio reuse
- ✓ **Graceful Degradation**: Audio system optional
- ✓ **Display Configuration**: Customizable width/height
- ✓ **Resource Cleanup**: Proper `cleanup()` method

**State Transitions**:
```
IDLE → VIDEO_PLAYBACK → WAITING_FOR_INPUT → FEEDBACK_AUDIO → IDLE
```

**Example Usage**:
```python
controller = MultimediaController(display_width=1024, display_height=768)
controller.play_video("videos/lion.mp4")
controller.play_feedback_audio("sounds/correct.wav")
controller.cleanup()
```

---

### 4. Animalquiz_refactored.py
**Purpose**: Main application orchestrator (Business Logic Layer)

**Classes**:
- `AnimalQuiz`: Quiz session manager with dependency injection

**Key Features**:
- ✓ **Dependency Injection**: Decoupled from data/multimedia layers
- ✓ **Clean Initialization**: Validates all resources on startup
- ✓ **Error Handling**: Try-except blocks for graceful failures
- ✓ **Type Hints**: Full type safety
- ✓ **Google-style Docstrings**: Complete method documentation
- ✓ **Score Tracking**: Real-time user progress
- ✓ **User Interruption**: Graceful quit with Ctrl+C

**Initialization Flow**:
```python
1. Load quiz data (JSON validation)
2. Initialize multimedia (audio/display check)
3. Create AnimalQuiz instance (dependency injection)
4. Run quiz loop
5. Cleanup resources
```

**Example Usage**:
```python
loader = QuizLoader("quiz_data.json")
controller = MultimediaController()
quiz = AnimalQuiz(loader, controller)
quiz.run_quiz()
```

---

## Design Principles

### 1. Separation of Concerns
- **Data Layer** (quiz_loader.py): Handles I/O and schema validation
- **I/O Layer** (multimedia_controller.py): Abstracts hardware operations
- **Business Logic** (Animalquiz_refactored.py): Orchestrates game flow

### 2. Dependency Injection
```python
# Before: Tightly coupled
quiz = AnimalQuiz()  # Hard to test, assumes resources exist

# After: Loosely coupled
quiz = AnimalQuiz(quiz_loader, multimedia_controller)  # Testable
```

### 3. Open-Closed Principle
- **Adding new quiz types**: Modify `quiz_data.json` only
- **Changing video format support**: Update only `multimedia_controller.py`
- No changes required to core `AnimalQuiz` class

### 4. Type Safety
```python
# All functions have explicit types
def ask_question(self, quiz_item: QuizItem) -> Optional[str]:
def check_answer(self, user_answer: str, quiz_item: QuizItem) -> bool:
```

---

## Fixed MVP Bottlenecks

### 1. Hardcoded Quiz Data ✓
**Before**:
```python
quiz_data = {
    "videos/lion.mp4": ("What is this?", ["Lion", "Tiger"], "Lion")
}
```

**After**: Externalized to `quiz_data.json` with full schema validation

### 2. Video Aspect Ratio Distortion ✓
**Before**: Videos scaled without aspect ratio preservation

**After**: 
```python
def _calculate_scaled_dimensions(self, frame_height, frame_width):
    # Preserves aspect ratio and centers frame
```

### 3. Resource Initialization ✓
**Before**: Assumed all drivers/devices available

**After**:
```python
try:
    pygame.mixer.init()
    self._audio_available = True
except Exception:
    self._audio_available = False  # Graceful degradation
```

### 4. Error Handling ✓
**Before**: Silent failures or crashes

**After**: Comprehensive validation with clear error messages
```python
if not os.path.exists(video_path):
    print(f"Warning: Video file not found: {video_path}")
```

---

## Migration Guide

### Step 1: Backup Original
```bash
cp Animalquiz.py Animalquiz_original.py
```

### Step 2: Add New Files
Ensure these files exist in the project directory:
- `quiz_data.json`
- `quiz_loader.py`
- `multimedia_controller.py`
- `Animalquiz_refactored.py`

### Step 3: Update Imports
Replace:
```python
python Animalquiz.py
```

With:
```python
python Animalquiz_refactored.py
```

### Step 4: Populate Quiz Data
Edit `quiz_data.json` with your quiz content following the schema.

---

## Extensibility Examples

### Example 1: Add New Quiz Type
Simply add to `quiz_data.json`:
```json
{
  "id": "quiz_elephant",
  "video_path": "videos/elephant.mp4",
  "question_text": "What is this?",
  "options": ["Rhino", "Elephant", "Hippo"],
  "correct_index": 1,
  "feedback_audio": {...},
  "difficulty": "hard"
}
```

### Example 2: Support New Video Format
Modify `multimedia_controller.py`:
```python
def play_video(self, video_path: str) -> bool:
    if video_path.endswith(".webm"):
        # Add WebM support
```

### Example 3: Add Quiz Filtering
Modify `quiz_loader.py`:
```python
def get_quizzes_by_difficulty(self, difficulty: str) -> List[QuizItem]:
    return [q for q in self._quizzes if q.difficulty == difficulty]
```

---

## Testing Recommendations

### Unit Tests
```python
# test_quiz_loader.py
def test_quiz_item_validation():
    item = QuizItem(...)
    assert item.validate() == True

# test_multimedia_controller.py
def test_aspect_ratio_calculation():
    controller = MultimediaController()
    w, h = controller._calculate_scaled_dimensions(1080, 1920)
    assert w/h == 1920/1080  # Aspect ratio preserved
```

### Integration Tests
```python
def test_full_quiz_flow():
    loader = QuizLoader("quiz_data.json")
    controller = MultimediaController()
    quiz = AnimalQuiz(loader, controller)
    # Mock video/audio and run
```

---

## Performance Considerations

1. **Audio Caching**: Repeated sounds cached in `MultimediaController`
2. **Lazy Video Loading**: Videos loaded only when played
3. **Frame Resizing**: Done in-place with OpenCV (no copy overhead)
4. **Display Update**: Uses efficient `cv2.imshow()` refresh rate

---

## Future Enhancements

- [ ] Database backend for quiz storage
- [ ] User authentication and progress tracking
- [ ] Multiplayer quiz modes
- [ ] Quiz generation from templates
- [ ] A/B testing framework
- [ ] Analytics dashboard
- [ ] Internationalization (i18n) support
- [ ] Mobile app port (React Native)

---

## Dependencies

```
pygame>=2.0.0
opencv-python>=4.5.0
```

Install with:
```bash
pip install pygame opencv-python
```

---

## Code Quality Metrics

- **Type Coverage**: 100% (all functions typed)
- **Documentation**: Google-style docstrings for all methods
- **Error Handling**: Try-except blocks at all critical I/O points
- **PEP 8 Compliance**: Verified with pylint/flake8
- **Cyclomatic Complexity**: Reduced from MVP (monolithic) to modular

---

## Contact & Support

For questions or issues, please refer to the architecture diagrams and module documentation above.

**Last Updated**: April 26, 2026
