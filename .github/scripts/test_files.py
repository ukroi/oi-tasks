import json
import os
import re

# <lang>_<CCC>.pdf -- an ISO-639 language and an ISO-3166 alpha-3 country.  Most languages
# carry a two-letter ISO-639-1 code, but some exist only in ISO-639-2/3 and are three
# letters: Montenegrin is "cnr" and has no two-letter form at all.  So the name is parsed
# rather than sliced at fixed offsets, which is what limited this to two-letter codes.
# languages.json is still the whitelist deciding which pairs are allowed.
STATEMENT_NAME = re.compile(r'([a-z]{2,3})_([A-Z]{3})\.pdf')


def test_filenames():
    def make_error(text):
        print(text)
        assert False
    folder_dir = os.path.join(os.path.dirname(__file__), '../..')
    with open(os.path.join(folder_dir, '.github/data/languages.json'), 'r') as f:
        languages = json.load(f)
    statements_dir = os.path.join(folder_dir, 'statements')
    for contest in os.listdir(statements_dir):
        contest_path = os.path.join(statements_dir, contest)
        if os.path.isdir(contest_path):
            for year in os.listdir(contest_path):
                if year == '.DS_Store':
                    continue
                if not year.isdigit():
                    make_error('year folder is not int ' + year)
                if int(year) < 1980 or int(year) > 2030:
                    make_error('wrong year ' + year)
                year_path = os.path.join(contest_path, year)
                problems = 0
                max_problem = 0
                for problem in os.listdir(year_path):
                    if problem == '.DS_Store':
                        continue
                    if not problem.isdigit():
                        make_error('problem folder is not int ' + problem)
                    if int(problem) <= 0 or int(problem) > 8:
                        make_error('wrong problem ' + problem)
                    problems += 1
                    max_problem = max(max_problem, int(problem))
                    problem_path = os.path.join(year_path, problem)
                    has_isc = False
                    for statement in os.listdir(problem_path):
                        parts = statement.split('-')
                        if len(parts) != 4:
                            make_error('wrong filename ' + statement)
                        if parts[0] != contest:
                            make_error('wrong contest in filename ' + statement)
                        if parts[1] != year:
                            make_error('wrong year in filename ' + statement)
                        if parts[2] != problem:
                            make_error('wrong problem in filename ' + statement)
                        name = parts[3]
                        match = STATEMENT_NAME.fullmatch(name)
                        if not match:
                            make_error('wrong format of filename ' + statement)
                            continue
                        if name == 'en_ISC.pdf':
                            has_isc = True
                        language, country = match.group(1), match.group(2)
                        if language not in languages:
                            make_error('languages not found ' + statement)
                        if country not in languages[language]:
                            make_error('country not found ' + statement)
                    if not has_isc:
                        make_error('Does not have ISC version ' + problem_path)

                if max_problem != problems:
                    make_error('not consecutive problems')


