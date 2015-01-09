from __future__ import print_function

import re
import time

from devkb import logging
from devkb.models import db
from devkb.command import BaseCommand


class FindRepos(BaseCommand):

    def __init__(self, *arg, **kwargs):
        self.repo_regex = re.compile(
            r'https://github\.com/(?P<ownername>[\w.-]+)/(?P<reponame>[\w.-]+)')
        self.repo_count = 0
        self.repos = {}

    def help(self):
        return 'Find github repos in stackoveflow data'

    def add_arguments(self, parser):
        parser.add_argument(
            '-o', '--out', default='/var/lib/scrapyd/github_repos.txt', help='store github repos url list')
        parser.add_argument(
            '-k', '--skip', type=int, default=0, help='paginator opt: skip items')
        parser.add_argument(
            '-t', '--limit', type=int, default=0, help='paginator opt: limit items')

    def gen_github_repos(self, mrepos, tags):
        for fullname in mrepos:
            if fullname not in self.repos:
                self.repos[fullname] = 'https://github.com/%s' % fullname
                print(self.repos[fullname], file=self.repos_f)
                repo = db.github_repos.find_one({'fullname': fullname})
                if repo:
                    otags = set(repo.get('tags', []))
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
        self.logging_minitely()

    def logging_minitely(self):
        now_t = time.time()
        if (now_t - self.last_t) > 60:
            self.last_t = now_t
            logging.info('Proccessed %d github repos', self.repo_count)

    def run(self, args):
        self.last_t = time.time()
        self.repos_f = open(args.out, 'w')
        logging.info('Proccessed 0 github repos')
        for question in db.stackoverflow_questions.find(skip=args.skip, limit=args.limit):
            mrepos = []
            m = self.repo_regex.search(question['body'])
            if m:
                mrepos.append('%s/%s' % m.groups())
            for cmt in question['comments']:
                m = self.repo_regex.search(cmt)
                if m:
                    mrepos.append('%s/%s' % m.groups())
            for ans in question['answers']:
                m = self.repo_regex.search(ans['body'])
                if m:
                    mrepos.append('%s/%s' % m.groups())
                for cmt in question['comments']:
                    m = self.repo_regex.search(cmt)
                    if m:
                        mrepos.append('%s/%s' % m.groups())
            self.gen_github_repos(mrepos, question['tags'])
            if 'github_repos' in question:
                orepos = set(question['github_repos'])
                nrepos = set(mrepos)
                erepos = list(nrepos - orepos)
                if len(erepos) > 0:
                    db.stackoverflow_questions.update(question, {'$push': {'github_repos': {'$each': erepos}}})
            else:
                db.stackoverflow_questions.update(question, {'$set': {'github_repos': list(set(mrepos))}})

        for tag in db.stackoverflow_tags.find(skip=args.skip, limit=args.limit):
            mrepos = []
            m = self.repo_regex.search(tag['descr'])
            if m:
                mrepos.append('%s/%s' % m.groups())
            self.gen_github_repos(mrepos, [tag['name']])
            if 'github_repos' in tag:
                orepos = set(tag['github_repos'])
                nrepos = set(mrepos)
                erepos = list(nrepos - orepos)
                if len(erepos) > 0:
                    db.stackoverflow_tags.update(tag, {'$push': {'github_repos': {'$each': erepos}}})
            else:
                db.stackoverflow_tags.update(tag, {'$set': {'github_repos': list(set(mrepos))}})
        logging.info('Proccessed %d github repos', self.repo_count)
        self.repos_f.close()
