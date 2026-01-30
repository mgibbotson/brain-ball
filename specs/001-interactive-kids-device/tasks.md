# Tasks: Interactive Kids Device - Crawl Phase

**Input**: Design documents from `/specs/001-interactive-kids-device/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Unit tests are included to verify hardware abstraction and ensure constitution compliance (hardware abstraction layer principle).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project structure per implementation plan in src/
- [X] T002 Create requirements.txt with Python dependencies (adafruit-circuitpython-ili9341, adafruit-blinka, gpiozero, pytest, pytest-mock)
- [X] T003 [P] Create README.md with project overview and setup instructions
- [X] T004 [P] Create .gitignore for Python project (venv, __pycache__, *.pyc)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Create base error types in src/lib/__init__.py (HardwareError, UIError)
- [X] T006 [P] Create src/lib/photoresistor/__init__.py with package structure
- [X] T007 [P] Create src/lib/lcd/__init__.py with package structure
- [X] T008 [P] Create src/ui/__init__.py with package structure
- [X] T009 [P] Create src/app/__init__.py with package structure
- [X] T010 [P] Create src/playground/__init__.py with package structure
- [X] T011 [P] Create tests/unit/ directory structure
- [X] T012 [P] Create tests/integration/ directory structure
- [X] T013 [P] Create tests/playground/ directory structure

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Photoresistor Light Interaction (Priority: P1) 🎯 MVP

**Goal**: A child can interact with the device by covering or exposing the photoresistor to light, and the device responds with visual feedback on the LCD display.

**Independent Test**: A child can cover the photoresistor with their hand or expose it to light, and the device responds by changing what is displayed on the LCD screen. This can be tested independently by having a child experiment with light levels and observing the display changes.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T014 [P] [US1] Create unit test for PhotoresistorInterface in tests/unit/test_photoresistor.py
- [X] T015 [P] [US1] Create unit test for LCDInterface in tests/unit/test_lcd.py
- [X] T016 [P] [US1] Create unit test for UIInterface in tests/unit/test_ui.py
- [X] T017 [P] [US1] Create unit test for LightState entity in tests/unit/test_light_state.py
- [X] T018 [P] [US1] Create unit test for DisplayContent entity in tests/unit/test_display_content.py
- [X] T019 [US1] Create unit test for light interaction logic in tests/unit/test_light_interaction.py

### Implementation for User Story 1

#### Hardware Abstraction Layer

- [X] T020 [P] [US1] Create PhotoresistorInterface abstract base class in src/lib/photoresistor/interface.py
- [X] T021 [P] [US1] Create LCDInterface abstract base class in src/lib/lcd/interface.py
- [X] T022 [P] [US1] Create UIInterface abstract base class in src/ui/interface.py
- [X] T023 [US1] Create PhotoresistorHardware implementation in src/lib/photoresistor/hardware.py (depends on T020)
- [X] T024 [US1] Create PhotoresistorMock implementation in src/lib/photoresistor/mock.py (depends on T020)
- [X] T025 [US1] Create LCDHardware implementation in src/lib/lcd/hardware.py using adafruit-circuitpython-ili9341 (depends on T021)
- [X] T026 [US1] Create LCDMock implementation in src/lib/lcd/mock.py (depends on T021)
- [X] T027 [US1] Create UIDesktop implementation in src/ui/desktop.py using Pygame (depends on T022)
- [X] T028 [US1] Create UIDevice implementation in src/ui/device.py using LCD interface (depends on T022, T025)

#### Data Models

- [X] T029 [P] [US1] Create LightState class in src/app/light_state.py
- [X] T030 [P] [US1] Create DisplayContent class in src/app/display_content.py

#### Application Logic

- [X] T031 [US1] Create light interaction logic in src/app/light_interaction.py (depends on T029, T030, T020, T021)
- [X] T032 [US1] Create main application loop in src/app/main.py (depends on T031, T027, T028)
- [X] T033 [US1] Add command-line argument parsing for --backend (desktop/device) in src/app/main.py
- [X] T034 [US1] Add error handling and graceful degradation for hardware failures in src/app/main.py
- [X] T035 [US1] Add logging for light level changes and display updates in src/app/light_interaction.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. A child can interact with the photoresistor and see visual feedback on the LCD display.

---

## Phase 4: Interactive Playgrounds

**Purpose**: Independent device testing tools for debugging and validation

- [X] T036 [P] Create photoresistor playground in src/playground/photoresistor_playground.py
- [X] T037 [P] Create LCD playground in src/playground/lcd_playground.py
- [X] T038 [P] Create playground test examples in tests/playground/test_playground_examples.py

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect the entire application

- [X] T039 [P] Update README.md with usage instructions and hardware setup
- [X] T040 [P] Add docstrings to all public classes and functions
- [X] T041 Code cleanup and refactoring (ensure functions < 50 lines per constitution)
- [X] T042 [P] Create integration test for hardware integration in tests/integration/test_hardware_integration.py
- [X] T043 Run quickstart.md validation - verify all setup steps work
- [X] T044 [P] Add type hints to all function signatures for better code clarity

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3)**: Depends on Foundational phase completion
- **Playgrounds (Phase 4)**: Depends on User Story 1 completion (uses hardware libraries)
- **Polish (Phase 5)**: Depends on all previous phases being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories

### Within User Story 1

- Tests (T014-T019) MUST be written and FAIL before implementation
- Hardware interfaces (T020-T022) before implementations (T023-T028)
- Data models (T029-T030) before application logic (T031-T035)
- Hardware implementations before UI implementations
- Core implementation before integration

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T003, T004)
- All Foundational tasks marked [P] can run in parallel (T006-T013)
- All test tasks for User Story 1 marked [P] can run in parallel (T014-T018)
- Hardware interface tasks can run in parallel (T020-T022)
- Data model tasks can run in parallel (T029-T030)
- Hardware implementation tasks can run in parallel after interfaces (T023-T026)
- UI implementation tasks can run in parallel after interfaces (T027-T028)
- Playground tasks can run in parallel (T036-T037)
- Polish tasks marked [P] can run in parallel (T039, T040, T042, T044)

---

## Parallel Example: User Story 1

```bash
# Launch all interface definitions in parallel:
Task: "Create PhotoresistorInterface abstract base class in src/lib/photoresistor/interface.py"
Task: "Create LCDInterface abstract base class in src/lib/lcd/interface.py"
Task: "Create UIInterface abstract base class in src/ui/interface.py"

# Launch all data models in parallel:
Task: "Create LightState class in src/app/light_state.py"
Task: "Create DisplayContent class in src/app/display_content.py"

# Launch all hardware implementations in parallel (after interfaces):
Task: "Create PhotoresistorHardware implementation in src/lib/photoresistor/hardware.py"
Task: "Create PhotoresistorMock implementation in src/lib/photoresistor/mock.py"
Task: "Create LCDHardware implementation in src/lib/lcd/hardware.py"
Task: "Create LCDMock implementation in src/lib/lcd/mock.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add Playgrounds → Test independently → Deploy/Demo
4. Add Polish → Final validation → Deploy/Demo

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: Hardware interfaces and implementations
   - Developer B: Data models and application logic
   - Developer C: UI implementations
3. All components integrate for User Story 1

---

## Notes

- [P] tasks = different files, no dependencies
- [US1] label maps task to User Story 1 for traceability
- User Story 1 should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All hardware interactions must go through abstraction interfaces (constitution principle V)
- Functions should be < 50 lines (constitution principle IV)
