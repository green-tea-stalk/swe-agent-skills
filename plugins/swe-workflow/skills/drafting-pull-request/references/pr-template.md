# Pull Request Template & Specifications

This reference provides the canonical Pull Request title and body structure, placeholders, and specification rules conforming to **Conventional Commits 1.0.0** and automated release workflows (such as `release-please`).

---

## 1. PR Title Specification (`release-please` Compatible)

### Title Format
```text
<type>(<scope>)[!]: <imperative subject summary (max 50-72 chars)>
```

### Title Construction Rules
1. **`<type>` (SemVer Impact Derivation)**:
   - Inspect all commits on the branch against the base branch (from Step 1).
   - Inherit the **highest SemVer impact** present among the commits:
     - **MAJOR**: Any commit introducing breaking changes (`!` or `BREAKING CHANGE:`) → Use `feat!` or `fix!`.
     - **MINOR**: Contains at least one `feat` commit → Use `feat`.
     - **PATCH**: Contains bug fixes and no `feat` → Use `fix`.
     - **Neutral**: Only maintenance, docs, or tests → Use `docs`, `refactor`, `test`, `chore`, etc.
2. **`(<scope>)` (Component Attribution & Mandatory Scope Rule)**:
   - Derive `<scope>` directly from the underlying commit history on the branch.
   - Must be a lowercase `kebab-case` noun identifying the affected component or package (e.g. `swe-workflow`, `backend`, `auth`).
   - In repositories using component-based versioning or automated release tools (such as `release-please`), the scope determines which package/component receives the release notes and version bump upon squash merge. **Never omit the scope** (e.g., use `feat(backend): ...`, not `feat: ...`).
3. **`[!]:` (Breaking Change Indicator)**:
   - If the PR introduces breaking API changes, append `!` immediately before the colon (e.g. `feat(api)!: drop legacy endpoint`).
4. **`<subject>` (Imperative Summary)**:
   - Written in the imperative mood, present tense (e.g., `add drafting-pull-request skill`, NOT `added` or `adds`).
   - Lowercase start recommended.
   - No trailing period.

---

## 2. Standard PR Body Template

```markdown
## Summary
<!-- High-level bullet points summarizing the core objective and outcome -->
- <Brief summary point 1>
- <Brief summary point 2>

## Context & Motivation
<!-- Explains WHY this change was made, referencing user problem, requirements, or session background -->
<Paragraph explaining motivation and background>

## Key Design Decisions & Trade-offs
<!-- Objective rationale behind choices where multiple valid approaches existed (provided by decision-analyst) -->
- **<Decision Topic / Area>**:
  - **Selected Approach**: <Adopted solution>
  - **Alternative Considered**: <Alternative valid approach that would also satisfy requirements>
  - **Rationale & Trade-off**: <Why this was chosen over the alternative>

## Changes Made
<!-- Structured technical breakdown based on diff analysis -->
- **<Component/Area 1>**: <Description of modifications>
- **<Component/Area 2>**: <Description of modifications>

<!-- Include this section ONLY if this PR introduces breaking changes (SemVer MAJOR) -->
## Breaking Changes
- BREAKING CHANGE: <Detailed explanation of what broke and migration instructions for consumers>

## Related Issues
<!-- Links to GitHub Issues if applicable (e.g. Closes #123, Fixes #456, Relates to #789) -->
- Closes #<issue-number>

## Verification & Testing
<!-- Deterministic checks, tests run, or verification steps -->
- [x] <Validation step 1>
- [ ] <Verification step 2>

<!-- OMIT this entire details block if the conversation language is English -->
<details>
<summary><Flag/Emoji> Details / Summary in <Conversation Language></summary>

### <Summary in Conversation Language>
- <Localized summary point 1>
- <Localized summary point 2>

### <Context & Motivation in Conversation Language>
<Localized background and motivation derived from session log>

### <Key Decisions & Trade-offs in Conversation Language>
- **<Decision Topic>**:
  - **<Adopted Solution>**: <Localized details>
  - **<Alternative Considered>**: <Localized details>
  - **<Rationale & Trade-off>**: <Localized details>

### <Changes Made in Conversation Language>
- **<Component 1>**: <Localized details>
- **<Component 2>**: <Localized details>

### <Breaking Changes in Conversation Language (if applicable)>
- **破壊的変更**: <Localized breaking change explanation>

### <Related Issues in Conversation Language>
- Closes #<issue-number>

### <Verification in Conversation Language>
- <Localized test results>

</details>
```

---

## 3. Instructions for Agents

1. **Title Alignment**: Construct the PR title using Conventional Commits with mandatory scope derived from the underlying commits, compatible with `release-please` (e.g. `feat(swe-workflow): add drafting-pull-request skill`).
2. **Conversation Language Folding**:
   - If the user conversation is in English: Do NOT include the `<details>` block.
   - If the user conversation is in any other language (e.g. Japanese, French, Chinese, German, Spanish): Include the `<details>` block with full translations of summary, motivation, decisions, changes, breaking changes (if any), and verification.
3. **Issue Linking**: If an Issue number was found or referenced, use standard GitHub linking keywords (`Closes #<id>`, `Fixes #<id>`, or `Relates to #<id>`). If no issue exists, state `N/A`.
4. **Breaking Changes**: If breaking changes are introduced, ensure both the PR title has `!` (or `BREAKING CHANGE:` is in the body) so `release-please` accurately triggers a MAJOR version bump upon squash merge.
