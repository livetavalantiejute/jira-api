import requests
import json


def create(request, user_id):
    """
    Create a new Jira project.
    Gets API request object and user id from main()
    """
    key = input("Provide project key (e.g. 'SFT'): ").strip().upper() #keys are always uppercase
    name = input("Provide project name (e.g. 'Software board'): ").strip().lower()
    while True: 
        type = input("Provide type (Scrum or Kanban): ").strip().lower()
        if type not in ["scrum", "kanban"]:
            print("Input either Scrum or Kanban")
        else:
            break
    description = input("Provide description (optional): ").strip()

    #constructing payload
    #currently only Scrum and Kanban are available
    payload = json.dumps(
        {
            "assigneeType": "PROJECT_LEAD",
            "description": description,
            "key": key,
            "leadAccountId": user_id,
            "name": name,
            "projectTemplateKey": "com.pyxis.greenhopper.jira:gh-simplified-"
            + type
            + "-classic",
            "projectTypeKey": "software",
        }
    )
    #Sending POST request to Jira
    try:
        response = requests.request(
            "POST",
            request.url + "rest/api/2/project",
            data=payload,
            headers=request.headers,
            auth=request.auth,
        )
    except requests.exceptions.RequestException as e:
        print(str(e))

    try:
        key = response.json()['key']
    except KeyError:
        print("Something went wrong. Try again")
    else:
        print(f"Project {key} inserted successfully!")
