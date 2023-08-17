from dataclasses import dataclass
from tabulate import tabulate
import requests


@dataclass
class Project:
    id: str
    name: str
    key: str


class Projects:
    def __init__(self, url, headers, auth, projects = []):
        self.url = url
        self.headers = headers
        self.auth = auth
        self.projects = projects

    def __str__(self):
        return tabulate(self.projects, headers="keys", tablefmt="grid")
    
    @staticmethod
    def get_projects_data(url, headers, auth):
        try:
            all_projects = requests.request(
                "GET", url + "rest/api/2/project/search", headers=headers, auth=auth
            ).json()["values"]
        except Exception as e:
            print(str(e))
        return all_projects
    
    def get_projects(self):
        for project in self.get_projects_data(self.url, self.headers, self.auth):
            project_obj = Project(
                id=project["id"], name=project["name"], key=project["key"]
            )
            self.projects.append(project_obj)

    
    

