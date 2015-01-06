from __future__ import print_function

import re

from devkb import logging
from devkb.models import db


class FindRepos(object):

    def __init__(self, skip=0, limit=0, *arg, **kwargs):
        self.github_regexp = re.compile(
            r'https://github\.com/(?P<ownername>[\w.-]+)/(?P<reponame>[\w.-]+)')
        self.skip = skip
        self.limit = limit
        self.repo_count = 0

    def gen_github_repos(self, mrepos, tags):
        for m in set(mrepos):
            fullname = '%s/%s' % m.groups()
            repo = db.github_repos.find_one({'fullname': fullname})
            if repo:
                otags = set(repo['tags'])
                ntags = set(tags)
                etags = list(ntags - otags)
                if len(etags) > 0:
                    res = db.github_repos.update(repo, {'$push': {'tags': {'$each': etags}}})
                    if res:
                        logging.debug('Updated %s with tags %s', fullname, etags)
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

    def run(self):
        logging.info('Proccessed 0 github repos')
        for question in db.stackoverflow_questions.find(skip=self.skip, limit=self.limit):
            mrepos = []
            m = self.github_regexp.search(question['body'])
            if m:
                mrepos.append(m)
            for cmt in question['comments']:
                m = self.github_regexp.search(cmt)
                if m:
                    mrepos.append(m)
            for ans in question['answers']:
                m = self.github_regexp.search(ans['body'])
                if m:
                    mrepos.append(m)
                for cmt in question['comments']:
                    m = self.github_regexp.search(cmt)
                    if m:
                        mrepos.append(m)
            self.gen_github_repos(mrepos, question['tags'])
        for tag in db.stackoverflow_tags.find(skip=self.skip, limit=self.limit):
            mrepos = []
            m = self.github_regexp.search(tag['descr'])
            if m:
                mrepos.append(m)
            self.gen_github_repos(mrepos, [tag['name']])
        logging.info('Proccessed %d github repos', self.repo_count)
