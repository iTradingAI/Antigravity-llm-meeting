#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  offline_git_sync.sh bundle --output <file.bundle> [--branch <name>]
  offline_git_sync.sh patch  --output-dir <dir> [--base <ref>] [--head <ref>]

Commands:
  bundle   Create a git bundle that can be copied to a networked machine and pushed.
  patch    Create format-patch files for email/air-gap transfer.

Examples:
  offline_git_sync.sh bundle --output /tmp/meeting.bundle --branch work
  offline_git_sync.sh patch --output-dir /tmp/patches --base origin/main --head work
USAGE
}

require_repo() {
  git rev-parse --is-inside-work-tree >/dev/null
}

cmd_bundle() {
  local output=""
  local branch
  branch="$(git branch --show-current)"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --output)
        output="$2"; shift 2 ;;
      --branch)
        branch="$2"; shift 2 ;;
      *)
        echo "Unknown option: $1" >&2; usage; exit 2 ;;
    esac
  done

  [[ -n "$output" ]] || { echo "--output is required" >&2; exit 2; }

  git bundle create "$output" "$branch"
  echo "Bundle created: $output"
  echo "On connected machine:"
  echo "  git clone "$output" repo-from-bundle"
  echo "  cd repo-from-bundle && git remote add origin <github-url> && git push -u origin $branch"
}

cmd_patch() {
  local output_dir=""
  local base=""
  local head
  head="$(git branch --show-current)"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --output-dir)
        output_dir="$2"; shift 2 ;;
      --base)
        base="$2"; shift 2 ;;
      --head)
        head="$2"; shift 2 ;;
      *)
        echo "Unknown option: $1" >&2; usage; exit 2 ;;
    esac
  done

  [[ -n "$output_dir" ]] || { echo "--output-dir is required" >&2; exit 2; }
  mkdir -p "$output_dir"

  if [[ -n "$base" ]]; then
    git format-patch -o "$output_dir" "$base..$head"
  else
    git format-patch -o "$output_dir" "$head"
  fi

  echo "Patch files created in: $output_dir"
}

main() {
  require_repo
  [[ $# -ge 1 ]] || { usage; exit 2; }

  local cmd="$1"
  shift

  case "$cmd" in
    bundle) cmd_bundle "$@" ;;
    patch) cmd_patch "$@" ;;
    -h|--help|help) usage ;;
    *)
      echo "Unknown command: $cmd" >&2
      usage
      exit 2
      ;;
  esac
}

main "$@"
