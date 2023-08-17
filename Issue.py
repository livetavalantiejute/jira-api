from dataclasses import dataclass
import requests
import itertools

from helpers import bold
from tabulate import tabulate

@dataclass
class Issue:
    key: str
    summary: str
    description: str
    assignee: str
    created: str
    issue_type: str
    priority: str
    reporter: str
    status: str


class Issues:
    def __init__(self, url, headers, auth, id, issues = [], statuses = [], issues_by_status = []):
        self.url = url
        self.headers = headers
        self.auth = auth
        self.id = id
        self.issues = issues
        self.statuses = statuses
        self.issues_by_status = issues_by_status

    def print_board(self):
        for category in self.issues_by_status:
            print(bold(list(category.keys())[0]))
            for issue in category.values():
                if issue:
                    print(tabulate(issue, headers="keys", tablefmt="grid"))
                else:
                    print("No issues found in this status")

    @staticmethod
    def get_issues_data(url, headers, auth, id):
        try:
            return requests.request(
                "GET",
                url + f"rest/api/2/search?jql=project={id}&maxResults=1000",
                headers=headers,
                auth=auth,
            ).json()["issues"]
        except Exception as e:
            print(str(e))

    def get_issues(self):
        try:
            for issue in self.get_issues_data(self.url, self.headers, self.auth, self.id):
                issue_obj = Issue(
                    key=issue["key"],
                    summary = issue["fields"]["summary"],
                    description = issue["fields"]["description"],
                    assignee = issue["fields"]["assignee"]["displayName"],
                    created = issue["fields"]["creator"]["displayName"],
                    issue_type = issue["fields"]["issuetype"]["name"],
                    priority = issue["fields"]["priority"]["name"],
                    reporter = issue["fields"]["reporter"]["displayName"],
                    status = issue["fields"]["status"]["name"],
                )
                self.issues.append(issue_obj)
        except UnboundLocalError:
            print("Cannot find project")
    
    @staticmethod
    def get_statuses_data(url, headers, auth, id):
        try:
            return requests.request(
                "GET", url + f"rest/api/2/project/{id}/statuses", headers=headers, auth=auth
            ).json()[0]["statuses"]
        except Exception as e:
            print(str(e))

    def get_statuses(self):
        try:
            for status in self.get_statuses_data(self.url, self.headers, self.auth, self.id):
                self.statuses.append(status["name"])
        except KeyError:
            print("No id found")

    @staticmethod
    def sort_issues(issues):
        issues.sort(key=lambda item: item.status)

    def group_issues(self):
        self.sort_issues(self.issues)
        for key, category in itertools.groupby(self.issues, key=lambda item: item.status):
            self.issues_by_status.append({key: list(category)})

        for status in self.statuses:
            if not any(status in keys for keys in self.issues_by_status):
                self.issues_by_status.append({status: []})


    