#!/usr/bin/env bash
# Cut a release: bump the version, tag it, push, and publish a GitHub release
# whose notes are the matching CHANGELOG.md section.
#
#   ./release.sh minor --dry-run   # show the plan and the notes, change nothing
#   ./release.sh minor             # cut it for real
#
# Expects a "## [X.Y.Z]" section in CHANGELOG.md for the version being cut.
# Run with --dry-run first if you need to know what that number will be.

set -euo pipefail

die() {
    printf 'error: %s\n' "$*" >&2
    exit 1
}

LEVEL=${1:-}
DRY_RUN=false
if [[ ${2:-} == --dry-run ]]; then
    DRY_RUN=true
elif [[ -n ${2:-} ]]; then
    die "unknown argument '$2'"
fi

case $LEVEL in
    major | minor | patch) ;;
    *) die "usage: $0 <major|minor|patch> [--dry-run]" ;;
esac

cd "$(dirname "$0")"

command -v gh >/dev/null || die "gh is not installed"
gh auth status >/dev/null 2>&1 || die "gh is not authenticated; run 'gh auth login'"

BRANCH=$(git rev-parse --abbrev-ref HEAD)
[[ $BRANCH == main ]] || die "on branch '$BRANCH'; releases are cut from main"
[[ -z $(git status --porcelain --untracked-files=no) ]] ||
    die "working tree has uncommitted changes; commit them first"

# Untracked files are fine, but a stale or diverged main is not.
if git fetch --quiet origin main 2>/dev/null; then
    [[ -z $(git log --oneline origin/main..main) ]] ||
        die "local main has unpushed commits; push them first"
    [[ -z $(git log --oneline main..origin/main) ]] ||
        die "origin/main has commits you do not; pull first"
else
    printf 'warning: could not reach origin; skipping the up-to-date check\n' >&2
fi

VERSION=$(uv version --bump "$LEVEL" --dry-run --short)
TAG="v$VERSION"

if git rev-parse -q --verify "refs/tags/$TAG" >/dev/null; then
    die "tag $TAG already exists locally"
fi
if gh api "repos/{owner}/{repo}/git/refs/tags/$TAG" >/dev/null 2>&1; then
    die "tag $TAG already exists on the remote"
fi

# The release notes are the changelog section for this version, verbatim.
NOTES=$(awk -v version="$VERSION" '
    $0 ~ "^## \\[" version "\\]" { collecting = 1; next }
    /^## \[/ { collecting = 0 }
    collecting
' CHANGELOG.md | awk 'NF { started = 1 } started')

[[ -n $NOTES ]] ||
    die "CHANGELOG.md has no notes under '## [$VERSION]'; add that section first"

if $DRY_RUN; then
    printf 'would cut %s from %s\n\n%s\n' "$TAG" "$(git rev-parse --short HEAD)" "$NOTES"
    exit 0
fi

# Gate on the tests only. Ruff still reports pre-existing findings in this
# repo, so linting here would block every release until those are cleared.
printf 'running tests...\n'
uv run -m pytest -q

uv version --bump "$LEVEL" >/dev/null
git add pyproject.toml uv.lock
git commit --quiet --message "chore: version bump ($VERSION)"
git tag --annotate "$TAG" --message "$TAG"

git push --quiet origin main
git push --quiet origin "$TAG"

NOTES_FILE=$(mktemp)
trap 'rm -f "$NOTES_FILE"' EXIT
printf '%s\n' "$NOTES" >"$NOTES_FILE"
gh release create "$TAG" --title "$TAG" --notes-file "$NOTES_FILE"
