from helpers import bold

from Project import Projects
from Issue import Issues


def view(request):
    projects = Projects(request.url, request.headers, request.auth)
    projects.get_projects()

    print(projects)

    id = input(bold("Provide id of which board you want to view: ")).strip()

    issues = Issues(id=id)
    issues.get_issues(request)
    issues.get_statuses(request)
    issues.group_issues()

    issues.print_board()
