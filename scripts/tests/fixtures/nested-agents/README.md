# Mosaic Notes fixture

Synthetic documentation only. The nested test helper copies a fixed inventory
of reviewed sources into a new task-owned directory. No external project,
credentials, service, or packages are needed. See the GptClaw nested guide for
acceptance prompts and expected observations (do not paste answers into tasks).

## Verification

Review changed Markdown and relative-link targets by inspection. There is no
application command or build. All content is synthetic. The repository root
and nested files have intentionally distinct conventions for scope evaluation.

## Update and rollback

The synthetic fixture maintainer owns updates. Inspect Git status, reconcile
existing guidance, and use a reviewed feature branch. Versions record ancestry;
templates never synchronize active files. For rollback, inspect the exact
adoption/update commit and use a targeted Git revert, reconciling conflicts and
preserving unrelated later edits and uncommitted work. Verify the resulting
policy and use a fresh task to demonstrate restored instructions. A first
adoption revert removes only the introduced area file; adjust any required-file
check deliberately. Do not reset, clean, change global settings, or reload an
ongoing task. Clean only the confirmed task-owned fixture after saving evidence.
