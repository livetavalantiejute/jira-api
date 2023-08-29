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
        """Get id of a type from types list of dictionaries"""
        for t in types:
            if t["name"].lower() == property:
                return t["id"]


    def add_issue(self, request, project_id):
        """Add issue through POST"""
        #Get all priorities and issues, and validate with object parameter
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

        try:
            response = requests.request(
                "POST",
                request.url + "rest/api/2/issue",
                data=payload,
                headers=request.headers,
                auth=request.auth,
            )
        except requests.exceptions.RequestException as e:
            print(str(e))

        try:
            response_key = response.json()['key']
        except KeyError:
            print(f"Error adding a task. {response['errors']['summary']}")
        else:
            print(f"Successfully added {response_key}")

    @staticmethod
    def get_priorities(request, project_id):
        """Get all priorities for a project"""
        response = requests.request(
            "GET",
            request.url + "rest/api/2/priority/search?projectId=" + project_id,
            headers=request.headers,
            auth=request.auth
        )

        return response.json()["values"]
    
    @staticmethod
    def get_issue_types(request, project_id):
        """Get all issue types for a project and add it to a list of dictionaries"""
        query = {
            "projectId": project_id
        }

        try:
            response = requests.request(
                "GET",
                request.url+"rest/api/2/issuetype/project",
                headers=request.headers,
                params=query,
                auth=request.auth
            )
        except requests.exceptions.RequestException as e:
            print(str(e))

        types = []
        for type in response.json():
            types.append({
                "id": type["id"],
                "name": type["name"]
            })
        return types
    
    def get_transitions(self, request):
        """Get all transitions (statuses). Required when changing status"""
        try:
            return requests.request(
                "GET",
                request.url + f"rest/api/2/issue/{self.key}/transitions",
                headers=request.headers,
                auth=request.auth,
            ).json()["transitions"]
        except requests.exceptions.RequestException as e:
            print(str(e))

    def patch_edit(self, request, changed, project_id):
        """PUT request for an issue in project. Accepts request object, changed list of dictionaries and project id"""
        payload = {"fields": {}}
        for change in changed:
            for key, value in change.items():
                #remove _ from key - API accepts keys without underscores
                key = re.sub("_", "", key)
                match key:
                    case "priority":
                        #Get all priorities, validate and return priority id
                        priorities = self.get_priorities(request, project_id)
                        value = self.get_type(priorities, value)
                    case "issuetype":
                        #Get all issue types, validate and return issue type id
                        issue_types = self.get_issue_types(request, project_id)
                        value = self.get_type(issue_types, value)
                    case "assignee":
                        #Get user id of assignee only if it's not None
                        if value:
                            request_assignee = copy.deepcopy(request)
                            request_assignee.username = value
                            value = request_assignee.get_user_id()
                    case "reporter":
                        #Get user id of reporter
                        request_reporter = copy.deepcopy(request)
                        request_reporter.username = value
                        value = request_reporter.get_user_id()
                    case "status":
                        #Get transitions and return transition id
                        statuses = self.get_transitions(request)
                        value = self.get_type(statuses, value)
                if key in ["description", "summary"]:
                    #description and summary don't need keys
                    payload["fields"][key] = value
                elif key == "status":
                    #if the key is status, a POST request is sent to issue transitions
                    data = json.dumps({"transition": {"id": value}})
                    response = requests.request(
                        "POST",
                        request.url + "rest/api/3/issue/" + self.key + "/transitions",
                        data=data,
                        headers=request.headers,
                        auth=request.auth,
                    )
                    continue
                else:
                    #for all other keys, key is required
                    payload["fields"][key] = {}
                    payload["fields"][key]["id"] = value

        if payload:
            payload = json.dumps(payload)
            
            try:
                response = requests.request(
                    "PUT",
                    request.url + "rest/api/2/issue/" + self.key,
                    data=payload,
                    headers=request.headers,
                    auth=request.auth,
                )
            except requests.exceptions.RequestException as e:
                print(str(e))

        print(f"Successfully edited {self.key}!")


class Issues:
    """Class for all issues in project"""
    def __init__(
        self, id=""
    ):
        self.id = id
        self.issues = []
        self.statuses = []
        self.issues_by_status = []

    def print_board(self):
        """Print the board of project by status"""
        for category in self.issues_by_status:
            #Print bold status name
            print(bold(list(category.keys())[0]))
            for issue in category.values():
                if issue:
                    print(tabulate(issue, headers="keys", tablefmt="grid"))
                else:
                    print("No issues found in this status")

    @staticmethod
    def get_issues_data(url, headers, auth, id):
        """Get all issues for project"""
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
        """Populate issues object with project issues"""
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
        """Get all statuses for project"""
        try:
            return requests.request(
                "GET",
                url + f"rest/api/2/project/{id}/statuses",
                headers=headers,
                auth=auth,
            ).json()[0]["statuses"]
        except Exception as e:
            print(str(e))

    @classmethod
    def get_statuses(cls, request, id):
        """Get all statuses and populate self.statuses"""
        instance = cls()
        try:
            for status in instance.get_statuses_data(
                request.url, request.headers, request.auth, id
            ):
                if status not in instance.statuses:
                    instance.statuses.append(status)
        except KeyError:
            print("No id found")
        return instance.statuses

    @staticmethod
    def sort_issues(issues):
        """Sort issues by status"""
        issues.sort(key=lambda item: item.status)

    def group_issues(self):
        """Group issues by status"""
        self.sort_issues(self.issues)
        for key, category in itertools.groupby(
            self.issues, key=lambda item: item.status
        ):
            #Each status contains its issues
            self.issues_by_status.append({key: list(category)})

        #if no issues in statuses, status issues is empty
        for status in self.statuses:
            if not any(status in keys for keys in self.issues_by_status):
                self.issues_by_status.append({status: []})
