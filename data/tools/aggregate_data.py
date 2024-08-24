import os
import argparse
import pandas as pd

DATA_DIR = "/home/davide/git/innovation/rl-autoscaling/data/dataset/"


def main(args):
    df = pd.read_csv(
        os.path.join(DATA_DIR, args.filename)
    )
    df[args.ts_column] = pd.to_datetime(df[args.ts_column], format=args.ts_format)
    df = df.resample(
        args.aggregation,
        on=args.ts_column
    ).mean().rolling(3).fillna('mean')
    df.to_csv(
        os.path.join(
            DATA_DIR,
            f"{args.filename.replace('.csv', f'_agg_{args.aggregation}.csv')}"
        )
    )


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f", "--filename",
        required=True
    )
    parser.add_argument(
        "-tc", "--ts-column",
        default='Timestamp'
    )
    parser.add_argument(
        "-tf", "--ts-format",
        default='%d/%m%Y %H:%M:%S'
    )
    parser.add_argument(
        "-a", "--aggregation",
        default='30min'
    )
    return parser


if __name__ == '__main__':
    parser = get_parser()
    main(parser.parse_args())