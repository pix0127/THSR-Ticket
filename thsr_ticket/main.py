import sys

sys.path.append("./")

import argparse
from thsr_ticket.controller.booking_flow import BookingFlow


def handle_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--new", help="New reserve", action="store_true")
    parser.add_argument("-r", "--run", help="Auto run", action="store_true")
    return parser.parse_args()


def main():
    args = handle_args()
    flow = BookingFlow()
    if args.new:
        flow.add_new_reserve()
    if args.run:
        flow.auto_run()


if __name__ == "__main__":
    main()
