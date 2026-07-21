#!/usr/bin/env python3
"""Autonomous development workflow runner for Medicare-Synth.

Automates the process of running repository validation checks (linter, type checker,
and unit tests), staging/committing changes, pushing the active feature branch,
opening a pull request, and autonomously merging it into the main branch.
"""

import argparse
import json
import subprocess
import sys


def run_cmd(args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    """Helper to run a shell command and print outputs."""
    print(f"Running: {' '.join(args)}")
    result = subprocess.run(args, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip(), file=sys.stderr)
    if check and result.returncode != 0:
        print(f"Error: Command failed with code {result.returncode}", file=sys.stderr)
        sys.exit(result.returncode)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run local verification and autonomously push, PR, and merge to main."
    )
    parser.add_argument(
        "--commit-msg",
        type=str,
        default="feat: implement autonomous workflow script and reconcile docs",
        help="Commit message to use for git commit",
    )
    parser.add_argument(
        "--title",
        type=str,
        default="feat: implement autonomous workflow script and reconcile docs",
        help="Pull request title",
    )
    parser.add_argument(
        "--body",
        type=str,
        default="Automated PR created by the autonomous workflow script. Reconciles docs and adds workflow automation.",
        help="Pull request body",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate code and show git commands but do not commit, push, or merge",
    )
    parser.add_argument(
        "--skip-merge",
        action="store_true",
        help="Create the PR but skip the autonomous merge step",
    )

    args = parser.parse_args()

    # Step 1: Run verification checks
    print("=== Step 1: Running Linter (Ruff) ===")
    run_cmd(["uv", "run", "ruff", "check", "."])

    print("\n=== Step 2: Running Type Checker (BasedPyright) ===")
    run_cmd(["uv", "run", "basedpyright"])

    print("\n=== Step 3: Running Unit Tests (Pytest) ===")
    run_cmd(["uv", "run", "pytest"])

    print("\n✓ Verification checks passed successfully.")

    # Step 2: Git safety check
    branch_res = run_cmd(["git", "branch", "--show-current"])
    current_branch = branch_res.stdout.strip()
    if not current_branch:
        print("Error: Could not determine current git branch name.", file=sys.stderr)
        sys.exit(1)

    print(f"Active branch: {current_branch}")
    if current_branch in ("main", "master"):
        print("Error: Refusing to run workflow on base branch 'main/master'. Please checkout a feature branch.", file=sys.stderr)
        sys.exit(1)

    # Step 3: Git operations
    if args.dry_run:
        print("\n=== [Dry Run] Git Commit & Push ===")
        print("Would stage files: git add .")
        print(f"Would commit: git commit -m '{args.commit_msg}'")
        print("Would push: git push -u origin HEAD")
        print("\n=== [Dry Run] GitHub PR & Merge ===")
        print(f"Would create PR: gh pr create --title '{args.title}' --body '{args.body}'")
        if not args.skip_merge:
            print("Would autonomously merge PR: gh pr merge --merge --delete-branch")
        print("\n✓ Dry-run completed successfully.")
        return

    print("\n=== Step 4: Staging and Committing Changes ===")
    run_cmd(["git", "add", "."])
    # Check if there are changes to commit
    diff_check = subprocess.run(["git", "diff", "--quiet", "--cached"])
    if diff_check.returncode == 0:
        print("No changes staged to commit.")
    else:
        run_cmd(["git", "commit", "-m", args.commit_msg])

    print("\n=== Step 5: Pushing branch to Remote ===")
    run_cmd(["git", "push", "-u", "origin", "HEAD"])

    print("\n=== Step 6: Creating GitHub Pull Request ===")
    # Check if a PR already exists for this branch to avoid duplicates
    pr_check = subprocess.run(["gh", "pr", "view", "--json", "state,url"], capture_output=True, text=True)
    pr_url = ""
    if pr_check.returncode == 0:
        try:
            pr_data = json.loads(pr_check.stdout)
            if pr_data.get("state") == "OPEN":
                pr_url = pr_data.get("url", "")
                print(f"Existing open PR found: {pr_url}")
        except Exception:
            pass

    if not pr_url:
        pr_res = run_cmd(["gh", "pr", "create", "--title", args.title, "--body", args.body])
        # The output of gh pr create is the PR URL on success
        pr_url = pr_res.stdout.strip()
        print(f"Pull Request created: {pr_url}")

    # Step 7: Merge PR autonomously
    if args.skip_merge:
        print("\n✓ PR Handoff completed. Skipping autonomous merge as requested.")
        return

    print("\n=== Step 7: Autonomous Merge to main ===")
    # Attempt to merge the PR using gh CLI
    # We use --merge and --delete-branch to clean up the feature branch
    merge_args = ["gh", "pr", "merge", "--merge", "--delete-branch"]
    print(f"Merging PR: {pr_url}")
    run_cmd(merge_args)
    print("\n✓ PR successfully merged into main and remote branch deleted.")


if __name__ == "__main__":
    main()
