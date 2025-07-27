# Standard Operating Procedure: Script Line Count Ceilings Protocol

**Michael Banovac**

**June 29, 2025**

---

## I. Core Principle and Rationale

This document establishes a "line budget" for the single main.py script. The purpose of this protocol is to treat the self-imposed, single-file constraint as a measurable resource, thereby enforcing a high degree of discipline throughout the development cycle.

By setting defined limits, we ensure a constant focus on the foundational principles of the **Code Doctrine**, specifically **Precision**, **Performance**, and **Elegance**. These ceilings prevent feature creep and force us to create systems that are not just functional, but are also economical, efficient, and refined.

## II. Defined Ceilings

The following line count limits apply to the main.py file and include all code, comments, and blank lines.

- **Soft Ceiling: 2,500 Lines**
  - **Definition:** This threshold represents the point at which the game should be approaching a feature-complete state for its core design. Exceeding this limit signals a shift from feature implementation to code refinement.

- **Hard Ceiling: 4,000 Lines**
  - **Definition:** This is a firm upper boundary. Development must not exceed this limit. It serves as a final quality gate, forcing us to prioritize essential features and perfect existing systems rather than expand indefinitely.

## III. Strategic Development Phases

The project's development focus and priorities will shift as we approach and exceed these ceilings.

**Phase 1: Approaching the Soft Ceiling (Line Count: ~2,000 -- 2,500)**

- **Primary Objective:** Shift from creation to optimization.
- **Tactical Focus:**
  - **Intensive Code Review:** All existing functions and classes will be audited for efficiency and clarity.
  - **Algorithmic Refinement:** We will actively seek opportunities to improve the performance of key systems (e.g., procedural generation, pathfinding).
  - **Soft Feature Freeze:** No new major systems will be introduced. The focus is exclusively on completing and polishing already-planned features.
- **Guiding Principles:** **Precision** and **Performance**.

**Phase 2: Exceeding the Soft Ceiling (Line Count: > 2,500)**

- **Primary Objective:** Achieve design perfection and finalize the game.
- **Tactical Focus:**
  - **Code Economy:** For any new line of code considered, a commensurate effort will be made to refactor and reduce the line count elsewhere in the script.
  - **Hard Prioritization:** Any planned features that are not yet implemented will be rigorously evaluated. Non-essential features will be cut to preserve the integrity of the line budget.
  - **Final Polish:** The focus becomes perfecting the user experience and ensuring the final artifact is a masterclass in efficiency and design.
- **Guiding Principle:** **Elegance**.

---

*--- End of Standard Operating Procedure ---*