import sys
import os.path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def call_findrepos(args):
    from devkb.commands.findrepos import FindRepos
    cmd = FindRepos(skip=args.skip, limit=args.limit)
    cmd.run()

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Developer Knowledge Database Mining')

    subparsers = parser.add_subparsers(title='subcommands:', help='list valid subcommands here')
    pfindrepos = subparsers.add_parser('findrepos', help='Find github repos in stackoveflow data')
    pfindrepos.add_argument('-k', '--skip', type=int, default=0, help='paginator opt: skip items')
    pfindrepos.add_argument('-t', '--limit', type=int, default=0, help='paginator opt: limit items')
    pfindrepos.set_defaults(func=call_findrepos)

    args = parser.parse_args(sys.argv[1:])
    args.func(args)
