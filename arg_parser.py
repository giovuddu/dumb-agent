import argparse


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--verbose", action="store_true", help="print debug info to stdout"
    )

    parser.add_argument("prompt", help="prompt to send to model")

    return parser.parse_args()
