import argparse

from round_robin import RoundRobin


def describe(db: RoundRobin):
    print(db.c)


parser = argparse.ArgumentParser(
    "Utility used to print the content of a Round-Robin Database."
)

parser.add_argument("-f", "--file",
                    help="The path of the Round-Robin database.",
                    type=str, nargs=1)


args = parser.parse_args()

if args.file:
    output_file = args.file[0]
else:
    output_file = 'du.db'  # In the current directory


if __name__ == "__main__":
    rrdb = RoundRobin.read_from_disk(output_file)
    describe(rrdb)
