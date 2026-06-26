#!/usr/bin/env bash
# Regression check for vibe-project-foundation scaffolding.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TMP_ROOT="$(mktemp -d /tmp/vpf-verify.XXXXXX)"

cleanup() {
  rm -rf "$TMP_ROOT"
}
trap cleanup EXIT

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

TARGET="$TMP_ROOT/TestProject"
bash "$SKILL_DIR/scaffold.sh" "$TARGET" "TestProject" "一个 verifier 测试项目" "2026-06-26" >/tmp/vpf-verify-scaffold.out

[ -d "$TARGET/.git" ] || fail "missing git repository"

required_files=(
  ".gitignore"
  "AGENTS.md"
  "CLAUDE.md"
  "README.md"
  "app/README.md"
  "design/README.md"
  "docs/README.md"
  "docs/agent-guide.md"
  "docs/spec.md"
  "docs/progress.md"
  "docs/roadmap.md"
  "docs/handoff.md"
  "scratch/README.md"
)

for file in "${required_files[@]}"; do
  [ -f "$TARGET/$file" ] || fail "missing required file: $file"
done

tracked_count="$(git -C "$TARGET" ls-files | wc -l | tr -d ' ')"
[ "$tracked_count" -ge 20 ] || fail "too few tracked files: $tracked_count"

placeholder_count="$( (grep -R -E '\{\{PROJECT_NAME\}\}|\{\{ONE_LINER\}\}|\{\{DATE\}\}' "$TARGET" --exclude-dir=.git || true) | wc -l | tr -d ' ')"
[ "$placeholder_count" = "0" ] || fail "unreplaced placeholders: $placeholder_count"

ds_store_count="$(find "$TARGET" -name '.DS_Store' -type f | wc -l | tr -d ' ')"
[ "$ds_store_count" = "0" ] || fail ".DS_Store files copied: $ds_store_count"

printf 'scratch temp\n' > "$TARGET/scratch/tmp.txt"
normal_status="$(git -C "$TARGET" status --short)"
[ -z "$normal_status" ] || fail "scratch file should be ignored in normal status: $normal_status"

ignored_status="$(git -C "$TARGET" status --short --ignored)"
printf '%s\n' "$ignored_status" | grep -q '!! scratch/tmp.txt' || fail "scratch temp file not listed as ignored"

head_subject="$(git -C "$TARGET" log -1 --pretty=%s)"
[ "$head_subject" = "chore: 搭建开发前地基(TestProject)" ] || fail "unexpected commit subject: $head_subject"

mkdir -p "$TMP_ROOT/Existing"
printf 'keep\n' > "$TMP_ROOT/Existing/file.txt"
set +e
bash "$SKILL_DIR/scaffold.sh" "$TMP_ROOT/Existing" "Existing" "一句话" >/tmp/vpf-verify-nonempty.out 2>/tmp/vpf-verify-nonempty.err
nonempty_code=$?
set -e
[ "$nonempty_code" -eq 2 ] || fail "non-empty target should exit 2, got $nonempty_code"
[ "$(cat "$TMP_ROOT/Existing/file.txt")" = "keep" ] || fail "non-empty target file was modified"

set +e
bash "$SKILL_DIR/scaffold.sh" "$TMP_ROOT/BadDate" "BadDate" "一句话" "2026/06/26" >/tmp/vpf-verify-baddate.out 2>/tmp/vpf-verify-baddate.err
baddate_code=$?
set -e
[ "$baddate_code" -ne 0 ] || fail "bad date should fail"
[ ! -e "$TMP_ROOT/BadDate" ] || fail "bad date should not create target"

set +e
bash "$SKILL_DIR/scaffold.sh" "$TMP_ROOT/InvalidDate" "InvalidDate" "一句话" "2026-99-99" >/tmp/vpf-verify-invaliddate.out 2>/tmp/vpf-verify-invaliddate.err
invaliddate_code=$?
set -e
[ "$invaliddate_code" -ne 0 ] || fail "invalid calendar date should fail"
[ ! -e "$TMP_ROOT/InvalidDate" ] || fail "invalid calendar date should not create target"

echo "OK: vibe-project-foundation scaffold verified"
