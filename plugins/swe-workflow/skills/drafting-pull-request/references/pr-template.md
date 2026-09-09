# Pull Request Template & Specifications

This reference provides the canonical Pull Request title and body structure, placeholders, and specification rules conforming to **Conventional Commits 1.0.0** and automated release workflows (such as `release-please`).

---

## 1. PR Title Specification (`release-please` Compatible)

### Title Format
```text
{type}({scope})[!]: {imperative subject summary (max 50-72 chars)}
```

### Title Construction Rules
1. **`{type}` (SemVer Impact Derivation)**:
   - Inspect all commits on the branch against the base branch (from Step 1).
   - Inherit the **highest SemVer impact** present among the commits:
     - **MAJOR**: Any commit introducing breaking changes (`!` or `BREAKING CHANGE:`) → Use `feat!` or `fix!`.
     - **MINOR**: Contains at least one `feat` commit → Use `feat`.
     - **PATCH**: Contains bug fixes and no `feat` → Use `fix`.
     - **Neutral**: Only maintenance, docs, or tests → Use `docs`, `refactor`, `test`, `chore`, etc.
2. **`({scope})` (Component Attribution & Mandatory Scope Rule)**:
   - Derive `{scope}` directly from the underlying commit history on the branch.
   - Must be a lowercase `kebab-case` noun identifying the affected component or package (e.g. `swe-workflow`, `backend`, `auth`).
   - In repositories using component-based versioning or automated release tools (such as `release-please`), the scope determines which package/component receives the release notes and version bump upon squash merge. **Never omit the scope** (e.g., use `feat(backend): ...`, not `feat: ...`).
3. **`[!]:` (Breaking Change Indicator)**:
   - If the PR introduces breaking API changes, append `!` immediately before the colon (e.g. `feat(api)!: drop legacy endpoint`).
4. **`{subject}` (Imperative Summary)**:
   - Written in the imperative mood, present tense (e.g., `add drafting-pull-request skill`, NOT `added` or `adds`).
   - Lowercase start recommended.
   - No trailing period.

---

## 2. Standard PR Body Template

```markdown
## Summary
<!--
NARRATIVE RECIPE (1 concise paragraph, strictly 3-4 sentences total):
1. Problem / Why (1-2 sentences): Explain the context, motivation, or limitation that made this change necessary.
2. Solution / What (1-2 sentences): Explain how this PR resolves it and the high-level outcome.

PERSPECTIVE & RULES:
- Write strictly in third-person objective, PR-centric voice (e.g. "This pull request...", "This change...").
- NEVER use first-person pronouns ("I", "my", "we", "our") or AI agent meta-actions ("I investigated...", "The agent updated...").
- DO NOT list file paths, diff line ranges, or individual commit logs. Leave implementation inspection to Files Changed.
- DO NOT use bullet points in this section.
-->
{Single 3-4 sentence narrative paragraph: Problem/Why (1-2 sentences) + Solution/What (1-2 sentences), starting with "This pull request ..."}

## Key Design Decisions & Trade-offs
<!--
Record genuine architectural decisions where multiple viable approaches existed (provided by decision-analyst).
If no non-trivial design decisions or alternatives were involved, state "- None (straightforward implementation following existing patterns)".
-->
- **{Decision Topic / Area}**:
  - **Selected Approach**: {Adopted solution and its key mechanism}
  - **Alternative Considered**: {Alternative valid approach that would also satisfy requirements}
  - **Rationale & Trade-off**: {Why this was chosen over the alternative}

<!-- Include this section ONLY if this PR introduces breaking changes (SemVer MAJOR). Otherwise, OMIT this entire section. -->
## Breaking Changes
- BREAKING CHANGE: {Detailed explanation of what broke and migration instructions for consumers}

## Related Issues
<!--
Link GitHub issues using closing keywords if applicable.
Options: Closes #{id}, Fixes #{id}, Relates to #{id}, or None.
-->
- {Closes #{issue-number} | Fixes #{issue-number} | Relates to #{issue-number} | None}

## Verification & Testing
<!--
Record the actual deterministic tests, static checks, or manual verifications executed prior to drafting the PR.
Specify actual commands executed and their observed outcomes (e.g. test suite pass counts, exit status).
If no manual verification was performed, omit the Manual Verification subsection.
-->
- **Automated Tests / Checks**:
  - `{actual command executed}`: `{observed outcome / pass count / exit status}`
- **Manual Verification** (if applicable):
  - `{concrete verification action}`: `{observed result or confirmation}`

<!-- OMIT this entire details block if the conversation language is English -->
<details>
<!--
Syntax: <summary>{flag} {Native "Translation" Label} ({English Language Name} Translation)</summary>
- {flag}: Country or regional flag emoji matching the conversation language (e.g. 🇯🇵, 🇫🇷, 🇩🇪, 🇨🇳, 🇪🇸)
- {Native "Translation" Label}: Localized "Translation" label in the native script (e.g. 日本語訳, Traduction française, Deutsche Übersetzung, 中文翻译)
- {English Language Name}: Name of the language in English (e.g. Japanese, French, German, Chinese, Spanish)
-->
<summary>{flag} {Native "Translation" Label} ({English Language Name} Translation)</summary>

<!--
Translate ALL above English sections into the active conversation language, strictly mirroring the identical heading structure:
- ## {Localized "Summary" Heading}
  {Localized translation of the 3-4 sentence narrative}
- ## {Localized "Key Design Decisions & Trade-offs" Heading}
  {Localized translation of decisions, or "- None"}
- ## {Localized "Breaking Changes" Heading} (Include ONLY if present in the English section above)
  {Localized translation of breaking changes}
- ## {Localized "Related Issues" Heading}
  {Localized translation of issue links, or "- None"}
- ## {Localized "Verification & Testing" Heading}
  {Localized translation of verification commands and results}
-->
{Full translation of all above sections into the active conversation language, strictly mirroring the English section structure}

</details>
```

---

## 3. Instructions for Agents

1. **Title Alignment**: Construct the PR title using Conventional Commits with mandatory scope derived from the underlying commits, compatible with `release-please` (e.g. `feat(swe-workflow): add drafting-pull-request skill`).
2. **Third-Person Narrative Summary**:
   - Write `## Summary` strictly in third-person objective voice (e.g., `This pull request ...`).
   - Follow the 2-part recipe: Problem/Why (1-2 sentences) + Solution/What (1-2 sentences) in a single concise paragraph (3-4 sentences total).
   - Never use first-person pronouns (`I`, `we`), AI meta-actions (`I fixed...`), or bullet lists in `## Summary`.
3. **No Diff Paraphrasing (`Changes Made` Elimination)**:
   - Do not include a `Changes Made` section. Leave individual file, class, and line inspections to GitHub's Files Changed diff.
4. **Architectural Decisions & Fallback**:
   - In `## Key Design Decisions & Trade-offs`, record genuine decisions where alternative designs existed.
   - If changes are straightforward with no architectural alternatives considered, record `- None (straightforward implementation following existing patterns)` or omit.
5. **Breaking Changes Omission**:
   - If breaking changes are introduced, ensure both the PR title has `!` (or `BREAKING CHANGE:` is in the body) so `release-please` accurately triggers a MAJOR version bump upon squash merge.
   - If no breaking changes exist, omit the entire `## Breaking Changes` section.
6. **Issue Linking**: If an Issue number was found or referenced, use standard GitHub linking keywords (`Closes #{id}`, `Fixes #{id}`, or `Relates to #{id}`). If no issue exists, state `None` (or `N/A`).
7. **Execution Evidence in Verification**:
   - In `## Verification & Testing`, record the actual deterministic commands executed by the agent during the task and their observed results (e.g., test suite pass counts, exit status, static checks).
   - If no manual verification was performed, omit the `Manual Verification` subsection.
8. **Conversation Language Folding (Full Translation Mirror)**:
   - If the user conversation is in English: Do NOT include the `<details>` block.
   - If the user conversation is in any other language (e.g. Japanese, French, Chinese, German, Spanish): Include the `<details>` block containing a full translation of all English sections, strictly mirroring the identical heading structure (Summary, Decisions, Breaking Changes if present, Related Issues, and Verification). Title must strictly conform to `<summary>{flag} {Native "Translation" Label} ({English Language Name} Translation)</summary>`.
