# Jira app 
This app uses JIRA API to fetch data from your Jira instance.
In this app you can:
* Create a new project
* Add a task to an existing project either from terminal, or from a file
* View the whole board with information, such as task name, assignee, description, etc.
* Edit an existing task
* Download comprehensive data of the whole project

## Installation
To use this app, install required dependencies with

*pip install -r requirements.txt*


Additionally, add your Jira API key in the enviroment file .env

## Usage
To open the app, call

*python main.py <YOUR_JIRA_INSTANCE_URL> <YOUR_JIRA_EMAIL>*


After that the available modes are shown:

**Create, View, Add, Edit, Done**

Input the mode key and follow instructions in the terminal.

The program runs until it is either interrupted, or exited - "done" is input.