from typing import List, Any

import os

import yaml
import jira
# noinspection PyProtectedMember
from jira.resources import Sprint, Issue


class Jira(object):

    CONFIG_FILE = "~/.jira.yaml"

    def __init__(self, user: str, apikey: str, server: str) -> None:
        self.user = user
        self.apikey = apikey
        self.server = server
        self.project = "AB"
        self.client = jira.JIRA(
            {"server": server}, basic_auth=(self.user, self.apikey)
        )

    def __getattr__(self, attr):
        return getattr(self.client, attr)

    @classmethod
    def from_config(cls, config_file: str = CONFIG_FILE) -> "Jira":
        with open(os.path.expanduser(config_file)) as f:
            conf = yaml.load(f)
        return cls(**conf)

    def search(self, jql, **kwargs: Any) -> List[Issue]:
        return self.client.search_issues(
            f"project={self.project} and {jql}", **kwargs
        )

    def active_sprints(self) -> List[Sprint]:
        first_board = self.boards()[0]
        return [
            sprint
            for sprint in self.sprints(first_board.id)
            if sprint.state == "ACTIVE"
        ]

    def log_time(self, issue: Issue, time_expr: str) -> None:
        self.add_worklog(issue, timeSpent=time_expr)
        issue.update()


def main():
    pass


if __name__ == "__main__":
    main()
