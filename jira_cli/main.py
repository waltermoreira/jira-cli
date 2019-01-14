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
        self.client = jira.JIRA({"server": server}, basic_auth=(self.user, self.apikey))

    def __getattr__(self, attr):
        return getattr(self.client, attr)

    @classmethod
    def from_config(cls, config_file: str = CONFIG_FILE) -> "Jira":
        with open(os.path.expanduser(config_file)) as f:
            conf = yaml.load(f)
        return cls(**conf)

    def search(self, jql, **kwargs: Any) -> List[Issue]:
        return self.client.search_issues(f"project={self.project} and {jql}", **kwargs)

    def all_sprints(self) -> List[Sprint]:
        first_board = self.boards()[0]
        return self.sprints(first_board.id)

    def active_sprints(self) -> List[Sprint]:
        return [sprint for sprint in self.all_sprints() if sprint.state == "ACTIVE"]

    def log_time(self, issue: Issue, time_expr: str) -> None:
        self.add_worklog(issue, timeSpent=time_expr)
        issue.update()

    def create_issue(
        self,
        summary: str,
        issue_type: str,
        assignee: str,
        sprint_name: str,
        epic: Issue,
    ) -> Issue:
        """Create a new issue.

        `sprint` is the first characters of the sprint name.
        """
        issue = self.client.create_issue(
            project=self.project, summary=summary, issuetype={"name": issue_type}
        )
        self.client.assign_issue(issue, assignee)
        sprint = [s for s in self.all_sprints() if s.name.startswith(sprint_name)][0]
        self.client.add_issues_to_sprint(sprint.id, [issue.key])
        self.client.add_issues_to_epic(epic.id, [issue.key])
        return issue


def main():
    pass


if __name__ == "__main__":
    main()
