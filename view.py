from helpers import bold
from tabulate import tabulate

from Project import Projects
from Issue import Issues


def view(request):
    projects = Projects(request.url, request.headers, request.auth)
    projects.get_projects()

    print(projects)

    id = input(bold("Provide id of which board you want to view: ")).strip()

    issues = Issues(request.url, request.headers, request.auth, id)
    issues.get_issues()
    issues.get_statuses()
    issues.group_issues()

    issues.print_board()
