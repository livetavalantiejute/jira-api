from helpers import bold

from Project import Projects
from Issue import Issues


def view(request, user_id):
    projects = Projects()
    projects.get_projects(request)

    id = projects.get_project_id()

    issues = Issues(id=id)
    issues.get_issues(request)

    issues.get_statuses(request, id)
    issues.group_issues()

    issues.print_board()

    return projects, id, issues
