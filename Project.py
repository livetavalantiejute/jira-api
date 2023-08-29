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
        """Get project data prom API"""
        try:
            all_projects = requests.request(
                "GET", request.url + "rest/api/2/project/search", headers=request.headers, auth=request.auth
            ).json()["values"]
        except Exception as e:
            print(str(e))
        return all_projects
    
    def get_projects(self, request):
        """Get all projects if projects is empty"""
        if not self.projects:
            for project in self.get_projects_data(request):
                project_obj = Project(
                    id=project["id"], name=project["name"], key=project["key"]
                )
                self.projects.append(project_obj)

    def project_validation(self, id):
        """Validate project by id"""
        if any(p.id == id for p in self.projects):
            return True
        else:
            print("Wrong project id\n")

    def get_project_id(self):
        """Get project id - get input and validate"""
        while True:
            print(self.__str__())
            project_id = input(bold("Project id: ")).strip().lower()
            if self.project_validation(project_id):
                return project_id
            

