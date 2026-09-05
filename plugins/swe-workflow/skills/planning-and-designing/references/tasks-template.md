---
feature: <feature-name>
document_type: tasks
version: 1.0.0
status: draft
updated_at: <YYYY-MM-DD>
upstream:
  requirements: 1.0.0
  design: 1.0.0
---

# Implementation Task Plan: <Feature Name>

<!--
Guidelines:
1. Executive PR Overview enables human reviewers to evaluate PR boundaries quickly.
2. Every task and acceptance criteria MUST use GFM checkboxes (`- [ ]` / `- [x]`) to serve as a persistent state machine for execution and recovery.
3. Every task MUST map back to both `REQ-xxx` and `COMP-xxx` in the Traceability Matrix.
4. Upstream versions MUST match latest requirements.md and design.md.
5. On revisions, if all tasks are completed, the plan may be reset and recreated for the new revision.
-->

## 1. Executive Stacked PR Overview

| PR # | Target Branch | Phase / Purpose | Key Components | Dependencies | Merge Order |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **PR 1** | `feat/<feature>-phase1-interfaces` | Core Interface & Contracts | `COMP-001`, `COMP-002` | `main` | 1 |
| **PR 2** | `feat/<feature>-phase2-core-logic` | Domain Logic & Storage | `COMP-002`, `COMP-003` | `PR 1` | 2 |
| **PR 3** | `feat/<feature>-phase3-cli-integration` | End-to-End Integration & CLI | `COMP-001` | `PR 2` | 3 |

---

## 2. Mechanical Traceability Matrix

Every active requirement and design component is accounted for with zero gaps:

| Requirement ID | Component ID | Implementation Task | Target PR | Status |
| :--- | :--- | :--- | :--- | :--- |
| **REQ-001** | `COMP-001` | `TASK-001` | PR 1 | Pending |
| **REQ-002** | `COMP-001` | `TASK-002` | PR 1 | Pending |
| **REQ-003** | `COMP-002` | `TASK-003` | PR 2 | Pending |
| **REQ-004** | `COMP-002` | `TASK-004` | PR 2 | Pending |
| **REQ-005** | `COMP-003` | `TASK-005` | PR 2 | Pending |
| **REQ-006** | `COMP-001`, `COMP-003` | `TASK-006` | PR 3 | Pending |

---

## 3. Stacked PR Task Specifications & Progress Tracker

Implementation agents execute tasks sequentially using the **Atomic Commit Loop**:
1. Pick the first unchecked task (`- [ ]`).
2. Implement code and passing unit/integration tests.
3. Mark task and criteria checkboxes as completed (`- [x]`).
4. Execute `committing-changes` to commit code and updated `tasks.md` atomically.
5. In case of unexpected interruption, resume immediately from the first unchecked task.

### PR 1: Core Interfaces & Contract Definitions
- **Branch**: `feat/<feature>-phase1-interfaces`
- **Merge Target**: `<default-branch>`

#### Tasks
- [ ] **TASK-001**: Define data models, schemas, and public signatures
  - **Component & Requirements**: `COMP-001`, `REQ-001`
  - **Target Files**: `src/models/<model-file>`, `tests/models/<test-file>`
  - **Acceptance Criteria**:
    - [ ] Input data validation rules (`minLength`, `enum`, etc.) defined.
    - [ ] Type signatures and export definitions verified.
    - [ ] Unit tests for data serialization and constraint validation pass.
  - **Commit Message**: `feat(<scope>): define COMP-001 data models and schemas`

- [ ] **TASK-002**: Implement interface contracts and precondition validators
  - **Component & Requirements**: `COMP-001`, `REQ-002`
  - **Target Files**: `src/contracts/<contract-file>`, `tests/contracts/<test-file>`
  - **Acceptance Criteria**:
    - [ ] Preconditions reject invalid input with explicit error types / RFC 9457 details.
    - [ ] Unit tests confirming caller obligation checks pass.
  - **Commit Message**: `feat(<scope>): implement COMP-001 interface contracts`

---

### PR 2: Domain Logic & Persistence
- **Branch**: `feat/<feature>-phase2-core-logic`
- **Merge Target**: `feat/<feature>-phase1-interfaces`

#### Tasks
- [ ] **TASK-003**: Implement core domain service logic and state invariants
  - **Component & Requirements**: `COMP-002`, `REQ-003`, `REQ-004`
  - **Target Files**: `src/services/<service-file>`, `tests/services/<test-file>`
  - **Acceptance Criteria**:
    - [ ] Domain logic fulfills postcondition guarantees.
    - [ ] State invariants preserved across normal and error execution paths.
    - [ ] Service unit tests achieve full branch coverage.
  - **Commit Message**: `feat(<scope>): implement COMP-002 domain service logic`

- [ ] **TASK-004**: Implement repository adapter and persistence
  - **Component & Requirements**: `COMP-003`, `REQ-005`
  - **Target Files**: `src/adapters/<adapter-file>`, `tests/adapters/<test-file>`
  - **Acceptance Criteria**:
    - [ ] Adapter satisfies repository interface contract.
    - [ ] Error mapping to domain exceptions verified.
    - [ ] Adapter integration tests pass.
  - **Commit Message**: `feat(<scope>): implement COMP-003 repository adapter`

---

### PR 3: End-to-End Integration & CLI
- **Branch**: `feat/<feature>-phase3-cli-integration`
- **Merge Target**: `feat/<feature>-phase2-core-logic`

#### Tasks
- [ ] **TASK-005**: Wire CLI commands / API endpoints with services
  - **Component & Requirements**: `COMP-001`, `COMP-003`, `REQ-006`
  - **Target Files**: `src/cli/<cli-file>`, `tests/e2e/<e2e-test-file>`
  - **Acceptance Criteria**:
    - [ ] CLI adheres to protocol: exit codes, stdio separation, signal handling.
    - [ ] End-to-end integration tests pass covering full scenarios.
  - **Commit Message**: `feat(<scope>): wire end-to-end CLI commands and integration`

---

## 4. Lifecycle & Reset Protocol

- **On Initial Creation**: All tasks are initialized as `- [ ]`.
- **On Specification Revision**:
  - If all tasks above are completed (`- [x]`), this plan is archived/reset and replaced with a clean list of new tasks for the revision diff.
  - If tasks are partially completed, active tasks are updated in place with realigned dependencies.

