import json
import os
import hashlib

import requests
from eolymp.ecm.content_pb2 import Content

from API import API

SPACE_ID = os.environ["SPACE_ID"]
USERNAME = os.environ["EOLYMP_USERNAME"]
PASSWORD = os.environ["EOLYMP_PASSWORD"]

api = API(space_id=SPACE_ID, username=USERNAME, password=PASSWORD)
folder_dir = os.path.join(os.path.dirname(__file__), '../..')

_sources = {}

def get_problem_sources():
    global _sources
    if len(_sources) > 0:
        return _sources
    problems = api.get_problems()
    sources = {}
    for problem in problems:
        problem_id = problem.id
        statements = api.get_statements(problem_id)
        en = None
        for statement in statements:
            if statement.locale == "en":
                en = statement
        sources[en.source] = sources.get(en.source, []) + [problem_id]
    print('Sources')
    print(sources)
    _sources = sources
    return sources


def get_languages():
    with open(os.path.join(folder_dir, '.github/data/languages.json'), 'r') as f:
        languages = json.load(f)
    print('Languages')
    print(languages)
    return languages


all_languages = get_languages()


def get_statements_from_folder(walk_path):
    statements = {}
    for (dir_path, dir_names, filenames) in os.walk(walk_path):
        for filename in filenames:
            if filename == ".DS_Store":
                continue
            name = filename.split('-')[-1]
            language = name[0:2]
            country = name[3:6]
            statements[language] = statements.get(language, []) + [(country, filename)]
    print('Statements from folder')
    print(statements)
    return statements


def get_statements(languages, walk_path):
    folder_statements = get_statements_from_folder(walk_path)
    statements = {}
    for lang in folder_statements:
        if len(folder_statements[lang]) == 1:
            ind = 0
        else:
            found = False
            for country in languages[lang]:
                for i in range(len(folder_statements[lang])):
                    if folder_statements[lang][i][0] == country:
                        found = True
                        ind = i
                        break
                if found:
                    break
        path = os.path.join(walk_path, folder_statements[lang][ind][1])
        statements[lang] = path
    print('Statements')
    print(statements)
    return statements


def get_link_from_file(path):
    name = path[path.rfind('/') + 1:]
    in_file = open(path, "rb")
    data = in_file.read()
    in_file.close()
    return api.upload_pdf(name, data)


def get_hash_of_file(path):
    in_file = open(path, "rb")
    data = in_file.read()
    in_file.close()
    return hashlib.sha256(data).hexdigest()


def update_eolymp_statements(prob_id, eolymp_statements, folder_statements):
    en = None
    api.set_problem_id(problem_id=prob_id)
    for statement in eolymp_statements:
        locale = statement.locale
        print('Working on', locale)
        if locale == 'en':
            en = statement
        if locale in folder_statements:
            path = folder_statements[locale]
            folder_hash = get_hash_of_file(path)
            eolymp_statement_name = ''
            if not hasattr(statement, 'download_link') or statement.download_link == '' or "static.eolymp.com" in statement.download_link:
                eolymp_hash = ''
            else:
                s = requests.get(statement.download_link)
                eolymp_hash = hashlib.sha256(s.content).hexdigest()
            if folder_hash != eolymp_hash:
                try:
                    statement.download_link = get_link_from_file(path)
                    print('Updating')
                    api.update_statement(prob_id, statement)
                except:
                    print("fail")
                    pass
            folder_statements[locale] = None
        else:
            # TODO DELETE ENGL - delete
            print('Deleting', prob_id, statement.id)
            api.delete_statement(prob_id, statement.id)

    for lang in folder_statements:
        if folder_statements[lang] is not None:
            print('Uploading', lang)
            api.create_statement(prob_id, lang, en.title, get_link_from_file(folder_statements[lang]), en.source)


def update_statement_with_problems(olymp, year, problems):
    for i in range(len(problems)):
        if olymp == 'IOI' and year == '2012':
            prob_ind = max(1, i - 3)
        else:
            prob_ind = i + 1
        prob_id = problems[i]
        print(prob_id)
        walk_path = os.path.join(folder_dir, 'statements', olymp.lower(), year, str(prob_ind))
        folder_statements = get_statements(all_languages, walk_path)
        eolymp_statements = api.get_statements(prob_id)
        update_eolymp_statements(prob_id, eolymp_statements, folder_statements)


def update_statement(olymp, year):
    source = olymp + ' ' + str(year)
    update_statement_with_problems(olymp, year, get_problem_sources()[source])


def run_script():
    sources = get_problem_sources()
    for source in list(sources)[-1:]: #TEMP, Last 1 only
        temp = source.split(' ')
        if len(temp) != 2:
            continue
        if len(temp[1]) != 4:
            continue
        olymp = temp[0]
        year = temp[1]
        update_statement_with_problems(olymp, year, sources[source])
    print('done')


if __name__ == "__main__":
    update_statement(os.environ["OLYMP"], os.environ["YEAR"])

