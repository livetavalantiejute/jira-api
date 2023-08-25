from dataclasses import dataclass
import requests
import itertools
import json
import copy

from helpers import bold
from tabulate import tabulate


@dataclass
class Issue:
    key: str = ""
    summary: str = ""
    description: str = ""
    assignee: str = ""
    created: str = ""
    issue_type: str = ""
    priority: str = ""
    reporter: str = ""
    status: str = ""

    def add_issue(self, request, project_id):
        priorities = self.get_priorities(request, project_id)
        priority_id = next((p["id"] for p in priorities if p["name"].lower() == self.priority), None)

        issue_types = self.get_issue_types(request, project_id)
        type_id = next((t["id"] for t in issue_types if t["name"].lower() == self.issue_type), None)

        request_assignee = copy.deepcopy(request)
        request_assignee.username = self.assignee
        assignee_id = request_assignee.get_user_id()

        payload = json.dumps(
            {
                "fields": {
                    "assignee": {"id": assignee_id},
                    "description": self.description,
                    "issuetype": {"id": type_id},
                    "priority": {"id": priority_id},
                    "project": {"id": project_id},
                    "reporter": {"id": request.get_user_id()},
                    "summary": self.summary,
                },
            }
        )

        response = requests.request(
            "POST",
            request.url + "rest/api/2/issue",
            data=payload,
            headers=request.headers,
            auth=request.auth,
        )

        print(
            json.dumps(
                json.loads(response.text),
                sort_keys=True,
                indent=4,
                separators=(",", ": "),
            )
        )

    @staticmethod
    def get_priorities(request, project_id):
        response = requests.request(
            "GET",
            request.url + "rest/api/2/priority/search?projectId=" + project_id,
            headers=request.headers,
            auth=request.auth
        )

        return response.json()["values"]
    
    @staticmethod
    def get_issue_types(request, project_id):
        query = {
            "projectId": project_id
        }
        response = requests.request(
            "GET",
            request.url+"rest/api/2/issuetype/project",
            headers=request.headers,
            params=query,
            auth=request.auth
        )

        types = []
        for type in response.json():
            types.append({
                "id": type["id"],
                "name": type["name"]
            })
        return types

class Issues:
    def __init__(
        self, id, issues=[], statuses=[], issues_by_status=[]
    ):
        # self.url = url
        # self.headers = headers
        # self.auth = auth
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

    def get_issues(self, request):
        try:
            for issue in self.get_issues_data(
                request.url, request.headers, request.auth, self.id
            ):
                issue_obj = Issue(
                    key=issue["key"],
                    summary=issue["fields"]["summary"],
                    description=issue["fields"]["description"],
                    assignee=issue["fields"]["assignee"]["displayName"],
                    created=issue["fields"]["creator"]["displayName"],
                    issue_type=issue["fields"]["issuetype"]["name"],
                    priority=issue["fields"]["priority"]["name"],
                    reporter=issue["fields"]["reporter"]["displayName"],
                    status=issue["fields"]["status"]["name"],
                )
                self.issues.append(issue_obj)
        except UnboundLocalError:
            print("Cannot find project")

    @staticmethod
    def get_statuses_data(url, headers, auth, id):
        try:
            return requests.request(
                "GET",
                url + f"rest/api/2/project/{id}/statuses",
                headers=headers,
                auth=auth,
            ).json()[0]["statuses"]
        except Exception as e:
            print(str(e))

    def get_statuses(self, request):
        try:
            for status in self.get_statuses_data(
                request.url, request.headers, request.auth, self.id
            ):
                self.statuses.append(status["name"])
        except KeyError:
            print("No id found")

    @staticmethod
    def sort_issues(issues):
        issues.sort(key=lambda item: item.status)

    def group_issues(self):
        self.sort_issues(self.issues)
        for key, category in itertools.groupby(
            self.issues, key=lambda item: item.status
        ):
            self.issues_by_status.append({key: list(category)})

        for status in self.statuses:
            if not any(status in keys for keys in self.issues_by_status):
                self.issues_by_status.append({status: []})
