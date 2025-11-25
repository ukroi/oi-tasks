import json

import requests
from eolymp.asset.asset_service_http import AssetServiceClient
from eolymp.asset.asset_service_pb2 import UploadFileInput
from eolymp.atlas import statement_service_pb2, statement_pb2
from eolymp.atlas.problem_service_http import ProblemServiceClient
from eolymp.atlas.problem_service_pb2 import ListProblemsInput
from eolymp.atlas.statement_pb2 import Statement
from eolymp.atlas.statement_service_http import StatementServiceClient
from eolymp.core.http_client import HttpClient
from eolymp.ecm import content_pb2
from eolymp.universe.space_service_pb2 import DescribeSpaceInput
from eolymp.universe.space_service_http import SpaceServiceClient


class API:
    def __init__(self, space_id, username, password):
        resp = requests.post(url='https://api.eolymp.com/oauth/token',
                             data={'username': username, 'password': password,
                                   'grant_type': 'password'})
        token = json.loads(resp.text)['access_token']
        client = HttpClient(token=token)
        u = SpaceServiceClient(client)
        space = u.DescribeSpace(DescribeSpaceInput(space_id=space_id)).space
        self.client = client
        self.space = space
        self.problem_client = ProblemServiceClient(client, url=space.url)
        self.asset = AssetServiceClient(client, url=space.url)
        self.statement_client = StatementServiceClient(client, url=space.url)

    def set_problem_id(self, problem_id):
        self.statement_client.url = self.space.url + "/problems/" + str(problem_id)

    def get_statements(self, prob_id):
        self.set_problem_id(problem_id=prob_id)
        return self.statement_client.ListStatements(statement_service_pb2.ListStatementsInput()).items

    def get_problems(self):
        def __get_problems(offset, size):
            return self.problem_client.ListProblems(request=ListProblemsInput(offset=offset, size=size))

        return get_many(__get_problems)

    def create_statement(self, prob_id, locale, title, link, source=""):
        self.set_problem_id(problem_id=prob_id)
        s = statement_pb2.Statement(locale=locale, title=title,
                                    content=content_pb2.Content(latex=" "), download_link=link, source=source)
        return self.statement_client.CreateStatement(
            statement_service_pb2.CreateStatementInput(statement=s)).statement_id

    def update_statement(self, problem_id, statement):
        self.set_problem_id(problem_id=problem_id)
        return self.statement_client.UpdateStatement(
            statement_service_pb2.UpdateStatementInput(statement_id=statement.id, statement=statement,
                                                       patch=[Statement.Patch.DOWNLOAD_LINK]))

    def delete_statement(self, problem_id, statement_id):
        self.set_problem_id(problem_id=problem_id)
        self.statement_client.DeleteStatement(statement_service_pb2.DeleteStatementInput(statement_id=statement_id))

    def upload_pdf(self, filename, data):
        t = self.asset.UploadFile(UploadFileInput(name=filename, type="application/pdf", data=data))
        return t.file_url


def get_many(f, item_filter=None):
    items = []
    offset = 0
    size = 100
    while True:
        m = f(offset=offset, size=size)
        for item in m.items:
            if item_filter is None or item_filter(item):
                items += [item]
        if len(m.items) != size:
            break
        offset += size
        print(offset)
    return items
