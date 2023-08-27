from dataclasses import dataclass
from tabulate import tabulate
import requests

from helpers import bold


@dataclass
class Project:
    id: str
    name: str
    key: str


class Projects:
    def __init__(self, projects = []):
        self.projects = projects

    def __str__(self):
        return tabulate(self.projects, headers="keys", tablefmt="grid")
    
    @classmethod
    def get_projects_data(self, request):
        try:
            all_projects = requests.request(
                "GET", request.url + "rest/api/2/project/search", headers=request.headers, auth=request.auth
            ).json()["values"]
        except Exception as e:
            print(str(e))
        return all_projects
    
    def get_projects(self, request):
        if not self.projects:
            for project in self.get_projects_data(request):
                project_obj = Project(
                    id=project["id"], name=project["name"], key=project["key"]
                )
                self.projects.append(project_obj)

    def project_validation(self, id):
        if any(p.id == id for p in self.projects):
            return True
        else:
            print("Wrong project id\n")

    def get_project_id(self):
        while True:
            print(self.__str__())
            project_id = input(bold("Project id: ")).strip().lower()
            if self.project_validation(project_id):
                return project_id
            

