<!--
Sync Impact Report:
- Version change: 1.1.0 → 2.0.0
- Modified principles: V. Incremental Development → I. Crawl-Walk-Run (NON-NEGOTIABLE)
- Added sections: Development Phases
- Removed sections: N/A
- Templates requiring updates:
  - ✅ plan-template.md (Constitution Check section exists)
  - ✅ spec-template.md (no constitution-specific references)
  - ✅ tasks-template.md (no constitution-specific references)
  - ✅ checklist-template.md (no constitution-specific references)
- Follow-up TODOs: None
-->

# Brain Ball Constitution

## Core Principles

### II. Simplicity First
**MUST**: Start with the simplest solution that works. Apply YAGNI (You Aren't Gonna Need It) strictly. Complexity MUST be justified with measurable benefits. Prefer explicit code over clever abstractions. **Rationale**: Prototype embedded devices have limited resources and tight timelines. Simple code is easier to debug, modify, and understand when hardware issues arise.

### III. Modular Architecture
**MUST**: All functionality MUST be organized into self-contained modules with clear interfaces. Modules MUST have single, well-defined responsibilities. Hardware-dependent code MUST be abstracted behind interfaces to enable testing. **Rationale**: Modular design allows easy swapping of components during prototyping, enables parallel development, and makes unit testing possible without hardware.

### IV. Clear and Readable Code
**MUST**: Code MUST be self-documenting through clear naming. Functions MUST be small and focused (ideally < 50 lines). Complex logic MUST be broken into smaller functions with descriptive names. Comments explain "why", not "what". **Rationale**: Embedded prototypes often require rapid iteration and debugging. Readable code reduces cognitive load and speeds up development cycles.

### V. Hardware Abstraction Layer
**MUST**: All hardware interactions (GPIO, sensors, communication protocols) MUST go through abstraction interfaces. Hardware drivers MUST be swappable without changing application logic. Mock implementations MUST be provided for testing. **Rationale**: Enables testing on host machines without hardware, allows easy hardware changes during prototyping, and isolates hardware bugs from application logic.

### I. Crawl-Walk-Run (NON-NEGOTIABLE)
**MUST**: Development MUST follow a strict crawl-walk-run progression. Start with the absolute minimum viable feature (crawl), get it working end-to-end, then incrementally add complexity (walk, then run). Each phase MUST be independently testable and deliverable. **Rationale**: Starting simple ensures we can get something working quickly, validate the approach, and build confidence before adding complexity. This prevents over-engineering and ensures each phase is stable before moving forward.

## Embedded Constraints

**MUST**: All code MUST account for embedded system limitations:
- Memory constraints: Stack and heap usage MUST be monitored
- Real-time requirements: Critical operations MUST meet timing constraints
- Power consumption: Sleep modes and power management MUST be considered
- Hardware failures: Code MUST handle sensor failures and communication errors gracefully
- Limited debugging: Code MUST be debuggable via serial output or minimal logging

## Development Phases

**MUST**: All features MUST be developed in phases:

- **Crawl Phase**: Absolute minimum viable feature. Single sensor, single interaction, single response. Get it working end-to-end before adding anything else.
- **Walk Phase**: Add one additional capability at a time. Each addition must be independently testable and stable before proceeding.
- **Run Phase**: Add remaining features and polish. Only after crawl and walk phases are stable.

**MUST**: Development MUST follow these practices:
- Code reviews verify constitution compliance before merge
- Hardware abstraction enables host-based unit testing
- Integration tests run on target hardware before deployment
- Documentation includes resource usage and timing characteristics
- Complexity additions require justification in code review

## Governance

This constitution supersedes all other development practices. Amendments require:
- Documentation of the change rationale
- Update to affected templates and documentation
- Version increment per semantic versioning rules
- All PRs and reviews MUST verify compliance with these principles

**Version**: 2.0.0 | **Ratified**: 2026-01-07 | **Last Amended**: 2026-01-07
