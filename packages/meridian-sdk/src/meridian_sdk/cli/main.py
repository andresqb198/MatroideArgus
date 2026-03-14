"""Meridian CLI — status, tail, test commands."""

from __future__ import annotations

import argparse
import sys


def cli() -> None:
    parser = argparse.ArgumentParser(prog="meridian", description="Meridian SDK CLI")
    subparsers = parser.add_subparsers(dest="command")

    # meridian status
    subparsers.add_parser("status", help="Check connection and show health status")

    # meridian tail
    subparsers.add_parser("tail", help="Stream latest predictions")

    # meridian test
    subparsers.add_parser("test", help="Send a synthetic prediction to verify setup")

    args = parser.parse_args()

    if args.command == "status":
        _cmd_status()
    elif args.command == "tail":
        _cmd_tail()
    elif args.command == "test":
        _cmd_test()
    else:
        parser.print_help()
        sys.exit(1)


def _cmd_status() -> None:
    from meridian_sdk.config import MeridianConfig

    config = MeridianConfig.from_env()
    print("Meridian SDK v0.1.0")
    print(f"  API URL:  {config.api_url}")
    print(f"  Project:  {config.project or '(not set)'}")
    print(f"  Env:      {config.env}")
    print(f"  API Key:  {'***' + config.api_key[-4:] if config.api_key else '(not set)'}")
    # TODO: actual health check request


def _cmd_tail() -> None:
    print("Streaming latest predictions... (not yet implemented)")


def _cmd_test() -> None:
    print("Sending synthetic prediction... (not yet implemented)")
