"""Command-line entry point: lead-funnel synth, check and report."""

import argparse
import re
import sys
import traceback
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from typing import NoReturn

from lead_funnel.load import LoadError, LoadResult, load_leads
from lead_funnel.metrics import default_week, parse_week, weekly_funnel
from lead_funnel.report import write_report
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
    result = load_leads(path)
    agencies = len({lead.agency for lead in result.leads})
    _print_summary(path.name, result, f"Kept {len(result.leads):,} leads across {agencies:,} agencies")
    return 0


def _report(args: argparse.Namespace) -> int:
    out, path = Path(args.out), Path(args.file)
    if out.is_file():
        return _error(f"--out {args.out} is a file, not a folder. Give a folder path.")
    result = load_leads(path)
    week = args.week or default_week(_today())
    funnel = weekly_funnel(result.leads, week)
    target = out / f"funnel-{week}.xlsx"
    try:
        write_report(funnel, result, path.name, out, args.force, datetime.now())
    except FileExistsError:
        return _error(f"{target} already exists. Use --force to replace it.")
    except PermissionError:
        return _error(f"cannot write {target}. Close it in Excel and try again.")
    if funnel.leads_in_week:
        note = "" if args.week else " (last complete week)"
        active = sum(1 for a in funnel.agencies if a.reached[0])
        week_line = f"Week {week}{note}: {funnel.leads_in_week:,} leads across {active:,} agencies"
    else:
        week_line = f"No leads in {week}; wrote an empty report"
    _print_summary(path.name, result, week_line, f"Wrote {target}")
    return 0


def _today() -> date:
    return date.today()


def _print_summary(name: str, result: LoadResult, *lines: str) -> None:
    counts = Counter(next(r for r in REASONS if reason.startswith(r)) for _, _, reason in result.rejected)
    rejected = f"Rejected {len(result.rejected):,} rows"
    if counts:
        rejected += " (" + ", ".join(f"{r}: {counts[r]:,}" for r in REASONS if counts[r]) + ")"
    print(f"Read {result.rows_read:,} rows from {name}")
    print(rejected)
    print(f"Removed {result.duplicates:,} duplicate lead ids")
    for line in lines:
        print(line)

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


def _week(text: str) -> str:
    try:
        parse_week(text)
    except ValueError:
        raise argparse.ArgumentTypeError("must look like 2026-W46") from None
    return text


class _Parser(argparse.ArgumentParser):
    """Usage errors follow DESIGN.md section 3: Error: <problem>. <fix>."""

    def error(self, message: str) -> NoReturn:
        message = re.sub(r"^argument (\S+): ", r"\1 ", message)
        self.exit(2, f"Error: {message}. Run {self.prog} --help for usage.\n")


def _parser() -> argparse.ArgumentParser:
    debug_help = "show the full error trace when something goes wrong"
    parser = _Parser(
        prog="lead-funnel", description="Check event lead exports, write weekly funnel reports in Excel, and generate fake leads for testing."
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

    report = commands.add_parser(
        "report",
        parents=[common],
        help="write the weekly per-agency funnel report in Excel",
        description="Load a lead export and write funnel-<week>.xlsx with per-agency counts, rates and a chart.",
        epilog="Example:\n  lead-funnel report data/sample/leads-seed42.csv --week 2026-W46 --out reports/",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    report.add_argument("file", help="lead export (.csv or .xlsx)")
    report.add_argument("--week", type=_week, help="ISO week like 2026-W46 (default: last complete week)")
    report.add_argument("--out", default="reports", help="folder for the report (default: reports)")
    report.add_argument("--force", action="store_true", help="replace the report if it already exists")
    report.set_defaults(run=_report)
    return parser
