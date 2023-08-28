from dataclasses import dataclass
import requests
import itertools
import json
import copy
import re

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
    parent: str = ""
    status: str = ""

    @classmethod
    def get_type(self, types, property):
        for t in types:
            if t["name"].lower() == property:
                return t["id"]


    def add_issue(self, request, project_id):
        priorities = self.get_priorities(request, project_id)
        priority_id = self.get_type(priorities, self.priority)

        issue_types = self.get_issue_types(request, project_id)
        type_id = self.get_type(issue_types, self.issue_type)

        payload = json.dumps(
            {
                "fields": {
                    "assignee": {"name": self.assignee},
                    "description": self.description,
                    "issuetype": {"id": type_id},
                    "priority": {"id": priority_id},
                    "project": {"id": project_id},
                    "reporter": {"id": request.get_user_id()},
                    "summary": self.summary,
                    "parent": {"key": self.parent if self.parent else None}
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

        response_key = response.json()['key']
        if response_key:
            print(f"Successfully added {response_key}")
        else:
            print(f"Error adding a task. {response['errors']['summary']}")

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
    

    def patch_edit(self, request, changed, project_id):
        payload = {"fields": {}}
        for change in changed:
            for key, value in change.items():
                key = re.sub("_", "", key)
                match key:
                    case "priority":
                        priorities = self.get_priorities(request, project_id)
                        value = self.get_type(priorities, value)
                    case "issuetype":
                        issue_types = self.get_issue_types(request, project_id)
                        value = self.get_type(issue_types, value)
                    case "assignee":
                        request_assignee = copy.deepcopy(request)
                        request_assignee.username = self.assignee
                        value = request_assignee.get_user_id()
                    case "status":
                        statuses = Issues.get_statuses(request, project_id)
                        value = self.get_type(statuses, self.status)
                    case "description" | "summary":
                        payload["fields"][key] = value
                    case _:
                        payload["fields"][key] = {}
                        payload["fields"][key]["id"] = value
        payload = json.dumps(payload)

        response = requests.request(
            "PUT",
            request.url + "rest/api/2/issue/" + self.key,
            data=payload,
            headers=request.headers,
            auth=request.auth,
        )

        print(f"Successfully edited {self.key}!")


class Issues:
    def __init__(
        self, id="", issues=[], statuses=[], issues_by_status=[]
    ):
        self.id = id
        self.issues = []
        self.statuses = []
        self.issues_by_status = []

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
                try:
                    parent_issue = issue["fields"]["parent"]["key"]
                except KeyError:
                    parent_issue = ""

                issue_obj = Issue(
                    key=issue["key"],
                    summary=issue["fields"]["summary"],
                    description=issue["fields"]["description"],
                    assignee=issue["fields"]["assignee"]["displayName"] if issue["fields"]["assignee"] else "",
                    created=issue["fields"]["creator"]["displayName"],
                    issue_type=issue["fields"]["issuetype"]["name"],
                    priority=issue["fields"]["priority"]["name"],
                    reporter=issue["fields"]["reporter"]["displayName"],
                    parent=parent_issue,
                    status=issue["fields"]["status"]["name"],
                )
                if issue_obj not in self.issues:
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

    # @classmethod
    def get_statuses(self, request, id):
        try:
            for status in self.get_statuses_data(
                request.url, request.headers, request.auth, id
            ):
                if status not in self.statuses:
                    self.statuses.append(status["name"])
        except KeyError:
            print("No id found")
        return self.statuses

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
