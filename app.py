import time

from dotenv import load_dotenv
import os
from services.repo_service import RepoService
from services.workflow_service import WorkflowService
from services.run_service import RunService
from entities.repo import Repo
from entities.workflow import Workflow
from entities.run import Run

load_dotenv()  # take environment variables from .env.
token = os.getenv('GITHUB_TOKEN')
username = os.getenv('USERNAME')
workflow_pattern = os.getenv('WORKFLOW_PATTERN')

repo_serv = RepoService(token, username)
workflow_serv = WorkflowService(token, username)
run_serv = RunService(token, username)


def get_repos(regex_pattern):
    repo_list = list()
    for rep in repo_serv.filter_repos(pattern=regex_pattern):
        repo_list.append(Repo(rep['id'], rep['name']))
    return repo_list


def get_secret_workflow(repo_name):
    res = workflow_serv.get_workflows(repo_name, workflow_pattern)[0]
    return Workflow(res['id'], res['name'])


def start_workflow(repo_name, workflow_id, access_key_id):
    return workflow_serv.dispatch_workflow(repo_name, workflow_id, access_key_id)


def get_run(repo_name):
    result = None
    for _ in range(5):
        time.sleep(30)
        res = workflow_serv.get_workflow_status(repo_name)['workflow_runs'][0]
        if len(res) > 0:
            result = Run(res['id'])
            break
    return result


def get_secrets(repo_name, run_id):
    run_serv.get_logs(repo_name, run_id)


if __name__ == '__main__':
    pattern_input = input('Ingrese el patron para filtrar repositorios: \n')
    access_key_id = input('Ingrese la llave a buscar: \n')
    output = {}
    for repo in get_repos(pattern_input):
        workflow = get_secret_workflow(repo.name)
        print(start_workflow(repo.name, workflow.id, access_key_id))
        run = get_run(repo.name)
        found_secrets = get_secrets(repo.name, run.id)
        print(found_secrets)
        output[repo.name] = found_secrets
    print(output)

    # repo = Repo(token, username)
    # workflow = Workflow(token, username)
    # run = Run(token, username)
    # repos = repo.filter_repos(pattern=pattern)
    # [print(repo['name']) for repo in repos]
    # workflows = workflow.get_workflows(repos[0]['name'], workflow_pattern)
    # [print(workflow) for workflow in workflows]
    # workflow.dispatch_workflow(repos[0]['name'], workflows[0]['id'], '1234567890')
    # print(workflow.get_workflow_status(repos[0]['name']))
    # repo_id = repos[0]['name']
    # for i in range(5):
    #     time.sleep(20)
    #     runs = workflow.get_workflow_status(repo_id)['workflow_runs']
    #     if len(runs) > 0:
    #         break
    # [print(run) for run in runs if run['name'] == 'secret workflow']
    # found_secrets = run.get_logs(repo_id, runs[0]['id'])
    # print(found_secrets)