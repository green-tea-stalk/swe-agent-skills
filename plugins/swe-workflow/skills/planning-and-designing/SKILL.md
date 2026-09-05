---
name: planning-and-designing
description: >-
  Use this skill when executing the Planning & Design phase (Phase A) of Spec-Driven Development (SDD).
  Engages in incremental requirements elicitation, checks task suitability, explores existing specifications
  for consolidation (duplicate, sub-scope, super-scope, new), verifies codebase feasibility to finalize inputs,
  drafts EARS/RFC 2119 requirements with Mermaid modeling, defines Component Contracts (DbC) and data models,
  extracts design decisions, creates GFM-tracked Stacked PR task plans, executes multi-stage subagent reviewer audits
  (up to 3 iterations), generates dynamic bilingual translations, and delegates to
  drafting-pull-request for atomic verification.
---

# Planning & Designing (SDD Phase A)

This skill guides the end-to-end execution of the Planning & Design phase of Spec-Driven Development (SDD). It transforms user requirements into rigorous, verifiable, and bilingual specification assets (`requirements.md`, `design.md`, `tasks.md`) stored under `docs/specs/<feature-name>/`.

---

## Workflow Protocol

Follow these sequential steps whenever planning and designing a new feature or specification revision:

```mermaid
flowchart TD
    subgraph P1["Phase 1: Requirements Elicitation & Suitability"]
        S1["Step 1: Incremental Requirements Elicitation<br>(Interactive dialogue until mutual completion)"] --> S2{"Step 2: Task Suitability Check<br>(Check heavyweight suitability & bypass confirmation)"}
        S2 -- "Bypass accepted" --> EXIT["Exit Skill (Proceed to Direct Implementation)"]
        S2 -- "Proceed with SDD" --> S3
    end

    subgraph P2["Phase 2: Spec Discovery & Consolidation"]
        S3["Step 3: Spec Exploration & Consolidation<br>(Duplicate, sub-scope, super-scope, or new feature)"] --> S4
    end

    subgraph P3["Phase 3: Codebase Reconnaissance & Input Finalization"]
        S4["Step 4: Codebase Reconnaissance & Feasibility<br>(Verify feasibility, fill gaps, finalize inputs)"] --> S5
    end

    subgraph P4["Phase 4: Specification Drafting & Review Audits"]
        S5["Step 5: Draft & Audit Requirements Specification<br>(requirements.md + requirements-reviewer)"] --> S6["Step 6: Draft & Audit Component Design<br>(design.md + decision-analyst + design-reviewer)"]
        S6 --> S7["Step 7: Draft & Audit Implementation Task Plan<br>(tasks.md + tasks-reviewer)"]
    end

    subgraph P5["Phase 5: Localization & PR Delegation"]
        S7 --> S8["Step 8: Bilingual Translation Generation<br>(Derive *.<lang>.md using ISO 639-1 code)"]
        S8 --> S9["Step 9: Delegate to drafting-pull-request<br>(Branch safety, atomic commit, draft PR creation)"]
    end
```

---

### Step 1: Incremental Requirements Elicitation

Users typically cannot convey full requirements in a single initial prompt. Step 1 conducts an interactive, multi-turn elicitation dialogue to crystallize ambiguous or high-level user ideas into robust requirements before any repository inspection occurs:

1. **Structured Elicitation Inquiries**:
   - Actively ask targeted questions to clarify:
     1. **Core Problem & Motivation**: What problem are we solving, and why?
     2. **Actors & Personas**: Who or what uses this feature (developers, end users, external services)?
     3. **Primary Use Cases**: What is the happy path and primary user journey?
     4. **Boundary & Edge Conditions**: What are the input constraints, rate limits, timeouts, and negative scenarios?
     5. **Out of Scope (Explicit Boundaries)**: What will we deliberately NOT implement in this iteration?

2. **Strict Mutual Exit Criteria (Fail-Closed)**:
   Step 1 MUST NOT complete until **both** conditions are satisfied:
   - **User Sign-off**: The user explicitly states that they have conveyed all initial requirements and have nothing further to add.
   - **Assistant Sufficiency Verification**: The assistant objectively verifies that necessary requirements information (motivation, primary actors, happy paths, edge cases, out-of-scope boundaries) is sufficiently clear to anchor formal specifications.
   - **Fail-Closed Rule**: If critical ambiguities or missing points remain, the assistant **MUST NOT terminate Step 1**, even if the user signals completion. The assistant must present the specific unaddressed questions and continue clarification. Step 1 is complete ONLY when both criteria are met.

---

### Step 2: Task Suitability Assessment & Bypass Decision

1. **Heavyweight Process Evaluation**:
   - SDD is a heavyweight process involving multi-stage formal modeling, DbC contracts, and multi-subagent auditing.
   - **Unsuitable Tasks**: Typo fixes, 1-2 line localized bug fixes, documentation typos, or trivial configuration tweaks.

2. **User Decision & Branch Control**:
   - If the task is identified as lightweight/trivial:
     - **Prompt the user**: "This task appears to be a lightweight or localized change. SDD is a heavyweight multi-stage process that introduces significant overhead for minor tweaks. We recommend proceeding with direct implementation and commit/PR creation instead. Would you like to bypass SDD, or do you still wish to generate formal specifications?"
     - **Bypass Accepted**: If the user accepts the bypass, **terminate the `planning-and-designing` skill gracefully** and proceed to direct code implementation.
     - **Bypass Declined (SDD Requested)**: If the user insists on formal specifications, continue the SDD process and proceed to Step 3.

---

### Step 3: Specification Exploration & Scope Consolidation

Once concrete requirements are elicited, inspect the full specification landscape under `docs/specs/` across the repository to determine the architectural topology and consolidation strategy:

1. **Analyze Existing Specification Topology**:
   Compare the elicited requirements against all existing specification directories under `docs/specs/` and classify into one of four patterns:
   - **Duplicate**: An existing spec covers the exact same scope -> Propose revising/updating the existing spec.
   - **Sub-scope**: The requirements represent a sub-feature or extension of an existing, broader spec -> Propose integrating into the existing spec as an added module or revision.
   - **Super-scope**: The requirements encompass or unify multiple smaller, existing specs -> Propose consolidating and superseding those existing specs.
   - **New Feature**: The requirements represent an entirely independent feature -> Establish a new feature directory.

2. **Mandatory User Confirmation & Decision Authority**:
   - Architectural and domain boundaries cannot always be determined mechanically.
   - The assistant **MUST present its topology findings and recommended consolidation strategy to the user and seek explicit confirmation**.
   - The assistant **MUST abide by the user's final decision** regarding whether to create a new spec or consolidate into an existing one.

3. **Normalize Feature Name & Determine Execution Mode**:
   - Normalize the confirmed feature name to lowercase kebab-case (`^[a-z0-9-]+$`, e.g. `user-authentication`, `csv-exporter`).
   - The canonical target directory is `docs/specs/<feature-name>/`.
   - Inspect `docs/specs/<feature-name>/` to determine mode:
     - **Initial Mode (0 existing files)**: Start at version `1.0.0`.
     - **Revision Mode (complete existing files exist)**: Inspect YAML frontmatter (`version`, `status`, `upstream`) and track revision type.
     - **Resume Mode (partial files exist)**: Resume execution from the first uncompleted step.

---

### Step 4: Codebase Reconnaissance & Technical Feasibility Verification

Ground the elicited requirements and architecture in the technical realities of the target codebase:

1. **Target Codebase Reconnaissance**:
   - **Guidelines**: Inspect `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, or repository guidelines if present.
   - **Tech Stack & Dependencies**: Inspect package manifests (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, etc.) to identify languages, runtime libraries, and testing frameworks.
   - **Existing Architecture Patterns**: Search for related modules, existing data models, interface patterns, and error handling conventions.

2. **Feasibility Verification & Gap-Filling Dialogue**:
   - Evaluate whether the elicited requirements are technically feasible within the existing codebase constraints.
   - If technical discrepancies, architectural trade-offs, or integration questions arise (e.g. choice of authentication library, database migration strategy), interview the user to resolve them.

3. **Strict Technical Exit Criteria (Fail-Closed)**:
   - The assistant MUST NOT terminate Step 4 until it objectively verifies that all technical prerequisites, architecture choices, and integration boundaries needed to draft `requirements.md`, `design.md`, and `tasks.md` are **completely determined and verified**.
   - Once all technical gaps are filled, the inputs for specification authoring are permanently **finalized**.

---

### Step 5: Draft & Audit Requirements Specification (`requirements.md`)

1. **Draft English SSOT**:
   - Create or update `docs/specs/<feature-name>/requirements.md` conforming strictly to [`references/requirements-template.md`](./references/requirements-template.md) using the finalized inputs.
   - Enforce standard EARS syntax patterns (Ubiquitous, Event-driven, State-driven, Unwanted behavior, Optional feature, Complex).
   - Apply uppercase RFC 2119 / RFC 8174 keywords (`MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, `MAY`).
   - Satisfy ISO/IEC/IEEE 29148:2018 quality characteristics (Unambiguous, Complete, Consistent, Verifiable, Traceable).
   - Include valid Mermaid diagrams (use cases or flowcharts) for human visual modeling.
   - Assign unique, immutable requirement IDs (`REQ-001`, `REQ-002`, etc.).

2. **Audit via `requirements-reviewer` Subagent (Max 3 Iterations)**:
   - **Invocation**: Invoke the dedicated `requirements-reviewer` subagent to audit `requirements.md`.
   - **Convergence**:
     - If `CHANGES_REQUIRED`: address all identified defects and re-audit (up to 3 total iterations).
     - If unresolved after 3 iterations: **HALT safely (Fail-Closed)** and escalate specific blocker findings to the user.
     - Proceed to Step 6 only upon receiving **APPROVED**.

---

### Step 6: Draft & Audit Architecture & Component Design (`design.md`)

1. **Draft English SSOT**:
   - Create or update `docs/specs/<feature-name>/design.md` conforming strictly to [`references/design-template.md`](./references/design-template.md).
   - Set frontmatter `upstream.requirements` to match the approved `requirements.md` version.
   - **Component Boundaries**: Define component IDs (`COMP-001`, `COMP-002`, etc.) covering external exposed interfaces (CLI, API) and major internal software boundaries (classes, domain services, repositories). Exclude private implementation details.
   - **Data Models**: Specify input/output schemas using standard JSON Schema constraint vocabulary (`type`, `required`, `minLength`, `maximum`, `pattern`, `enum`).
   - **Protocols**: Specify transport protocols, CLI exit codes, HTTP status mappings, timeouts, and retry policies.
   - **Design by Contract (DbC)**: Express Preconditions, Postconditions, and Invariants using uppercase RFC 2119 / 8174 keywords.
   - **Error Handling**: Specify RFC 9457 Problem Details for external interfaces and structured exception hierarchies for internal components.
   - **Visual Modeling**: Include Mermaid sequence diagrams and/or state machines.

2. **Extract Design Decisions via `decision-analyst` Subagent**:
   - Invoke the `decision-analyst` subagent to extract non-trivial architectural decisions and trade-offs.
   - Embed extracted decisions into Section 7 of `design.md`.

3. **Audit via `design-reviewer` Subagent (Max 3 Iterations)**:
   - Invoke the dedicated `design-reviewer` subagent to audit `design.md`.
   - Enforce fail-closed convergence (max 3 iterations; escalate if unresolved).
   - Proceed to Step 7 only upon receiving **APPROVED**.

---

### Step 7: Draft & Audit Implementation Task Plan (`tasks.md`)

1. **Draft English SSOT**:
   - Create or update `docs/specs/<feature-name>/tasks.md` conforming strictly to [`references/tasks-template.md`](./references/tasks-template.md).
   - Set frontmatter `upstream.requirements` and `upstream.design` to match current versions.
   - **Executive PR Overview**: Provide a structured summary of planned Stacked PRs, target branches, scope, and merge order for human review.
   - **Traceability Matrix**: Complete mapping table covering `REQ-xxx` × `COMP-xxx` × `TASK-xxx` × `PR-x` with zero gaps.
   - **Progress Tracking State Machine**: Format all tasks and acceptance criteria with GFM checkboxes (`- [ ]`).
   - **Atomic Commit Loop Readiness**: Ensure each task is structured for independent execution, testing, and atomic commit alongside `tasks.md`.
   - **Lifecycle on Revision**: If all previous tasks were completed, cleanly reset/recreate the task list for the new revision.

2. **Audit via `tasks-reviewer` Subagent (Max 3 Iterations)**:
   - Invoke the dedicated `tasks-reviewer` subagent to audit `tasks.md`.
   - Enforce fail-closed convergence (max 3 iterations; escalate if unresolved).
   - Proceed to Step 8 only upon receiving **APPROVED**.

---

### Step 8: Bilingual Translation Generation

Once all three English SSOT documents (`requirements.md`, `design.md`, `tasks.md`) achieve **APPROVED** status:
1. **Detect Conversation Language**:
   - If the active user conversation is in English, skip translation (the English SSOT documents are sufficient).
2. **Generate Localized Documents (Derived Translation)**:
   - If the conversation is in a non-English language:
     - Identify the ISO 639-1 language code of the user's active conversation (e.g. `ja` for Japanese, `zh` for Chinese, `fr` for French, `de` for German, `es` for Spanish, etc.).
     - Generate `requirements.<lang>.md` translating `requirements.md` using standard RFC 2119 / 8174 localized mapping for that language (e.g. for Japanese: `MUST` -> 「〜しなければならない」, `MUST NOT` -> 「〜してはならない」, `SHOULD` -> 「〜することが推奨される」, `MAY` -> 「〜してもよい」).
     - Generate `design.<lang>.md` translating `design.md` while maintaining code signatures and translating contract clauses.
     - Generate `tasks.<lang>.md` translating `tasks.md` preserving checkbox states and matrix structure.
   - Maintain identical frontmatter versions and `upstream` references across language pairs.

---

### Step 9: Delegate to `drafting-pull-request`

Do NOT perform manual Git branching or piecemeal commits during this skill. Instead, delegate the finalized assets to the existing `drafting-pull-request` skill within the same plugin:

1. **Execute `drafting-pull-request`**:
   - The `drafting-pull-request` skill automatically inspects branch safety, switches to an appropriate feature branch if on a protected branch, groups uncommitted specification files into an atomic Conventional Commit (`docs(specs): add planning and design specification for <feature-name>`), and creates a GitHub Draft PR with folded bilingual details.
2. **Review Output**:
   - Confirm Draft PR URL and present the completed specification assets and PR link to the user for human review.

