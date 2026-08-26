# drafting-pull-request

Use this skill when creating a new draft pull request or updating an existing PR on GitHub.

## Features
- Inspects repository state, uncommitted changes, branch safety, and remote sync using `scripts/prepare_pr.py`.
- Formats `release-please` compatible PRs with localized folding.
- Integrates with the `decision-analyst` subagent to extract objective design decisions and trade-offs.

## Related Subagent: `decision-analyst`
A dedicated software architect expert specialized in analyzing session logs and diffs to extract objective, high-value design decisions and architectural trade-offs while strictly filtering out bugs, hallucinations, and obvious choices.
