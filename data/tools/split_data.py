import os
import argparse
import pandas as pd

DATA_DIR = "/home/davide/git/innovation/rl-autoscaling/data/dataset/"


def main(args):
    df = pd.read_csv(
        os.path.join(DATA_DIR, args.filename)
    )
    train_df = df[df[args.column] <= args.split]
    train_df.to_csv(
        os.path.join(
            DATA_DIR,
            f"{args.filename.replace('.csv', f'_train.csv')}"
        )
    )
    test_df = df[df[args.column] > args.split]
    test_df.to_csv(
        os.path.join(
            DATA_DIR,
            f"{args.filename.replace('.csv', f'_test.csv')}"
        )
    )


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f", "--filename",
        required=True
    )
    parser.add_argument(
        "-s", "--split",
        default='2018-01-01 00:00:00'
    )
    parser.add_argument(
        "-c", "--column",
        default='Timestamp'
    )
    parser.add_argument(
        "-t", "--test-size",
        default=0.3
    )
    return parser


if __name__ == '__main__':
    parser = get_parser()
    main(parser.parse_args())