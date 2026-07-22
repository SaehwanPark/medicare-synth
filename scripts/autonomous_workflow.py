#!/usr/bin/env python3
"""Autonomous development workflow runner for Medicare-Synth.

Automates the process of running repository validation checks (linter, type checker,
and unit tests), staging/committing changes, pushing the active feature branch,
opening a pull request, and autonomously merging it into the main branch.
"""

import argparse
import sys
from medicare_synth.workflow import run_autonomous_workflow


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run local verification and autonomously push, PR, and merge to main."
    )
    parser.add_argument(
        "--commit-msg",
        type=str,
        default="feat: implement autonomous workflow subcommand and reconcile docs",
        help="Commit message to use for git commit",
    )
    parser.add_argument(
        "--title",
        type=str,
        default="feat: implement autonomous workflow subcommand and reconcile docs",
        help="Pull request title",
    )
    parser.add_argument(
        "--body",
        type=str,
        default="Automated PR created by the autonomous workflow engine. Reconciles docs and adds CLI auto-workflow subcommand.",
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
    parser.add_argument(
        "--validation-check",
        action="store_true",
        help="Verify dataset relational validation integrity before commit/push",
    )
    parser.add_argument(
        "--evidence-check",
        action="store_true",
        help="Verify ResDAC Knowledge Base evidence snapshot contracts before commit/push",
    )

    args = parser.parse_args()

    exit_code = run_autonomous_workflow(
        commit_msg=args.commit_msg,
        title=args.title,
        body=args.body,
        dry_run=args.dry_run,
        skip_merge=args.skip_merge,
        validation_check=args.validation_check,
        evidence_check=args.evidence_check,
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
