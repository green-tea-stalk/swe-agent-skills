# Conventional Commit Message Template

This reference provides the canonical commit message structure, placeholders, and specification rules conforming to **Conventional Commits 1.0.0** and automated release workflows (such as `release-please`).

---

## Standard Commit Template

```text
{type}({scope})[!]: {imperative subject summary (max 50-72 chars)}

{body: explain WHY this change was made, referencing user requests, design decisions, and contrast with previous behavior. Blank line before body is REQUIRED.}

[BREAKING CHANGE: {description of breaking changes (SemVer MAJOR). Blank line before footers is REQUIRED.}]
[{Issue-Token}: #{issue-number} (e.g. Closes #123, Fixes #456)]
Co-Authored-By: {AgentName} {ModelName} <{email}>
```

---

## Structural Elements & Specification Rules

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" are interpreted as described in RFC 2119.

### 1. Header: `{type}({scope})[!]: {subject}`

- **`{type}` (REQUIRED)**:
  - Commits MUST be prefixed with a type consisting of a noun.
  - `feat`: Adds a new feature to the codebase (correlates with SemVer **MINOR**).
  - `fix`: Patches a bug in the codebase (correlates with SemVer **PATCH**).
  - Additional allowed types (SemVer neutral unless paired with a breaking change):
    - `refactor`: Code change that neither fixes a bug nor adds a feature.
    - `perf`: Performance improvement.
    - `test`: Adding or correcting tests.
    - `docs`: Documentation only changes.
    - `style`: Formatting, whitespace, semi-colons (no code logic change).
    - `build`: Build system or external dependency changes.
    - `ci`: CI configuration files and scripts.
    - `chore`: Maintenance tasks, repo tooling, housekeeping.
    - `revert`: Reverts a previous commit (reference the commit SHA in the footer).

- **`({scope})` (OPTIONAL in standard spec, REQUIRED in component-tracked / monorepo projects)**:
  - A scope MAY be provided after a type, surrounded by parenthesis `({scope})`.
  - Must consist of a noun describing a section of the codebase in lowercase `kebab-case` (e.g., `swe-workflow`, `backend`, `auth`, `api`, `cli`).
  - In projects using component-level versioning or automated release tools (such as `release-please`), the scope MUST be specified so changes are correctly attributed to the specific package or component.

- **`[!]:` Breaking Change Indicator (REQUIRED for breaking changes, otherwise omitted)**:
  - A breaking change MUST be indicated by a `!` immediately before the terminal colon (e.g. `feat!:`, `feat(api)!:`) or as an entry in the footer.
  - Correlates with SemVer **MAJOR**.
  - If `!` is used, `BREAKING CHANGE:` MAY be omitted from the footer, and the commit description SHALL describe the breaking change.

- **`: ` Separator (REQUIRED)**:
  - A terminal colon followed by a single space MUST immediately follow the type/scope/`!` prefix.

- **`{subject}` (REQUIRED)**:
  - A short summary of the code changes MUST immediately follow the colon and space.
  - Written in the imperative mood, present tense (e.g., `add user authentication`, NOT `added` or `adds`).
  - Lowercase start recommended.
  - No trailing period.
  - Target maximum length: 50–72 characters.

### 2. Body: `{body: explain WHY...}`

- **Blank Line (REQUIRED)**:
  - A commit body MAY be provided and MUST begin one blank line after the description.
- **Content & Structure**:
  - Free-form, newline-separated paragraphs.
  - Focus on the **Why**: Explain motivation, problem context, user requests, architectural decisions, and contrast with previous behavior.
  - Do NOT merely restate what the code diff shows.

### 3. Footers: `[BREAKING CHANGE:]`, `[{Issue-Token}]`, `Co-Authored-By:`

- **Blank Line (REQUIRED)**:
  - One or more footers MAY be provided and MUST begin one blank line after the body (or one blank line after the description if body is omitted).
- **Git Trailer Format**:
  - Each footer follows the Git trailer format (`{token}: {value}` or `{token} #{value}`).
  - A footer token MUST use `-` in place of whitespace characters (e.g., `Co-Authored-By`, `Reviewed-by`, `Refs`, `Closes`).
  - **Exception**: `BREAKING CHANGE` or `BREAKING-CHANGE` MUST be uppercase.
- **Breaking Change Footer**:
  - `BREAKING CHANGE: {description}` (Token MUST be uppercase). Triggers SemVer **MAJOR** bump.
- **Issue Linking**:
  - `Closes #{id}` or `Fixes #{id}` triggers automated issue closure on GitHub.
- **Co-Author Trailer**:
  - `Co-Authored-By: {AgentName} {ModelName} <{email}>`.
  - If the model name contains parentheses (e.g. `Gemini 3.1 Pro (High)`), enclose the author name in double quotes:
    `Co-Authored-By: "Antigravity Gemini 3.1 Pro (High)" <gemini@google.com>`

---

## Concrete Examples

### Example 1: Standard Feature with Component Scope
```text
feat(backend): implement token revocation endpoint

Add a dedicated revocation endpoint to invalidate active JWTs upon user logout.
Previously, tokens remained valid until expiration, creating a security window.

Closes #42
Co-Authored-By: "Antigravity Gemini 3.1 Pro (High)" <gemini@google.com>
```

### Example 2: Bug Fix with Scope
```text
fix(auth): correct token expiration timestamp calculation

Use UTC timestamp instead of local system time when computing token expiry.
Prevents premature token invalidation across daylight saving transitions.

Fixes #128
Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
```

### Example 3: Breaking Change with `!` and Footer
```text
feat(api)!: migrate auth endpoints to v2 schema

Drop legacy v1 token payload schema in favor of standardized OAuth2 token response.

BREAKING CHANGE: The `access_token_id` field has been removed; client applications must now parse `token_id` from the OAuth2 payload.
Closes #205
Co-Authored-By: Codex GPT-5.6 Sol <codex@openai.com>
```
