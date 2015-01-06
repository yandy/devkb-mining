from __future__ import print_function

import re

from devkb import logging
from devkb.models import db
from devkb.command import BaseCommand


class FindRepos(BaseCommand):

    def __init__(self, *arg, **kwargs):
        self.repo_regex = re.compile(
            r'https://github\.com/(?P<ownername>[\w.-]+)/(?P<reponame>[\w.-]+)')
        self.repo_count = 0

    def help(self):
        return 'Find github repos in stackoveflow data'

    def add_arguments(self, parser):
        parser.add_argument(
            '-k', '--skip', type=int, default=0, help='paginator opt: skip items')
        parser.add_argument(
            '-t', '--limit', type=int, default=0, help='paginator opt: limit items')

    def gen_github_repos(self, mrepos, tags):
        for m in set(mrepos):
            fullname = '%s/%s' % m.groups()
            repo = db.github_repos.find_one({'fullname': fullname})
            if repo:
                otags = set(repo['tags'])
                ntags = set(tags)
                etags = list(ntags - otags)
                if len(etags) > 0:
                    res = db.github_repos.update(
                        repo, {'$push': {'tags': {'$each': etags}}})
                    if res:
                        logging.debug(
                            'Updated %s with tags %s', fullname, etags)
                        self.repo_count += 1
            else:
                doc = {
                    'fullname': fullname,
                    'url': 'https://github.com/%s' % fullname,
                    'tags': tags
                }
                res = db.github_repos.insert(doc)
                if res:
                    logging.debug('Inserted %s', fullname)
                    self.repo_count += 1
            if self.repo_count != 0 and self.repo_count % 100 == 0:
                logging.info('Proccessed %d github repos', self.repo_count)

    def run(self, args):
        logging.info('Proccessed 0 github repos')
        for question in db.stackoverflow_questions.find(skip=args.skip, limit=args.limit):
            mrepos = []
            m = self.repo_regex.search(question['body'])
            if m:
                mrepos.append(m)
            for cmt in question['comments']:
                m = self.repo_regex.search(cmt)
                if m:
                    mrepos.append(m)
            for ans in question['answers']:
                m = self.repo_regex.search(ans['body'])
                if m:
                    mrepos.append(m)
                for cmt in question['comments']:
                    m = self.repo_regex.search(cmt)
                    if m:
                        mrepos.append(m)
            self.gen_github_repos(mrepos, question['tags'])
        for tag in db.stackoverflow_tags.find(skip=args.skip, limit=args.limit):
            mrepos = []
            m = self.repo_regex.search(tag['descr'])
            if m:
                mrepos.append(m)
            self.gen_github_repos(mrepos, [tag['name']])
        logging.info('Proccessed %d github repos', self.repo_count)
