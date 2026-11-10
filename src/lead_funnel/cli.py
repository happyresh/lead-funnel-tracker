"""Command-line entry point: lead-funnel synth and lead-funnel check."""

import argparse
import sys
import traceback
from collections import Counter
from pathlib import Path

from lead_funnel.load import LoadError, LoadResult, load_leads
from lead_funnel.synth import generate_leads, write_csv

MAX_ROWS = 100_000
MAX_DETAIL_LINES = 20
REASONS = ("blank lead_id", "blank agency", "unknown stage", "bad date")


def main(argv: list[str] | None = None) -> int:
    """Run the CLI and return the exit code: 0 ok, 1 input error, 2 usage error, 3 unexpected error."""
    args = _parser().parse_args(argv)
    try:
        return args.run(args)
    except LoadError as err:
        return _error(str(err))
    except Exception:  # noqa: BLE001 - every unexpected error becomes exit 3 without a stack trace.
        if args.debug:
            traceback.print_exc()
        else:
            _error("something went wrong. Run with --debug for details.")
        return 3


def _synth(args: argparse.Namespace) -> int:
    try:
        write_csv(Path(args.out), generate_leads(args.rows, args.seed), force=args.force)
    except FileExistsError:
        return _error(f"{args.out} already exists. Use --force to replace it.")
    except PermissionError:
        return _error(f"cannot write {args.out}. Close it in other programs and try again.")
    print(f"Wrote {args.rows:,} leads to {args.out} (seed {args.seed})")
    return 0


def _check(args: argparse.Namespace) -> int:
    path = Path(args.file)
    _print_summary(path.name, load_leads(path))
    return 0


def _print_summary(name: str, result: LoadResult) -> None:
    counts = Counter(next(r for r in REASONS if reason.startswith(r)) for _, _, reason in result.rejected)
    rejected = f"Rejected {len(result.rejected):,} rows"
    if counts:
        rejected += " (" + ", ".join(f"{r}: {counts[r]:,}" for r in REASONS if counts[r]) + ")"
    agencies = len({lead.agency for lead in result.leads})
    print(f"Read {result.rows_read:,} rows from {name}")
    print(rejected)
    print(f"Removed {result.duplicates:,} duplicate lead ids")
    print(f"Kept {len(result.leads):,} leads across {agencies:,} agencies")

    details = [
        f"Row {row} ({lead_id}): {reason}" if lead_id else f"Row {row}: {reason}"
        for row, lead_id, reason in result.rejected
    ] + result.warnings
    sys.stdout.flush()  # Keep the summary above the details when both go to one terminal.
    for line in details[:MAX_DETAIL_LINES]:
        print(line, file=sys.stderr)
    if len(details) > MAX_DETAIL_LINES:
        print(f"...and {len(details) - MAX_DETAIL_LINES:,} more", file=sys.stderr)


def _error(message: str) -> int:
    print(f"Error: {message}", file=sys.stderr)
    return 1


def _rows(text: str) -> int:
    try:
        rows = int(text)
    except ValueError:
        rows = 0
    if not 1 <= rows <= MAX_ROWS:
        raise argparse.ArgumentTypeError(f"must be between 1 and {MAX_ROWS}")
    return rows


def _parser() -> argparse.ArgumentParser:
    debug_help = "show the full error trace when something goes wrong"
    parser = argparse.ArgumentParser(
        prog="lead-funnel", description="Check event lead exports and generate fake leads for testing."
    )
    parser.add_argument("--debug", action="store_true", help=debug_help)
    # SUPPRESS keeps a subcommand's missing --debug from resetting one given before the subcommand.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--debug", action="store_true", default=argparse.SUPPRESS, help=debug_help)
    commands = parser.add_subparsers(dest="command", required=True, metavar="command")

    synth = commands.add_parser(
        "synth",
        parents=[common],
        help="write a file of fake leads for testing",
        description="Write a CSV of obviously fake leads. The same seed always gives the same file.",
        epilog="Example:\n  lead-funnel synth --rows 500 --seed 42 --out data/sample/leads-seed42.csv",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    synth.add_argument("--out", required=True, help="CSV file to write")
    synth.add_argument("--rows", type=_rows, default=500, help=f"number of leads, 1 to {MAX_ROWS} (default 500)")
    synth.add_argument("--seed", type=int, default=42, help="random seed (default 42)")
    synth.add_argument("--force", action="store_true", help="replace the file if it already exists")
    synth.set_defaults(run=_synth)

    check = commands.add_parser(
        "check",
        parents=[common],
        help="check a lead export and summarize problems",
        description="Load a .csv or .xlsx lead export, then report rejected rows and duplicates.",
        epilog="Example:\n  lead-funnel check data/sample/leads-seed42.csv",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    check.add_argument("file", help="lead export (.csv or .xlsx)")
    check.set_defaults(run=_check)
    return parser
