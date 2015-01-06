import sys
import os.path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    from devkb.commands.extract_github_info import ExtracGithubInfo
    cmd = ExtracGithubInfo()
    cmd.run()
