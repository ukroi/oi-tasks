import json
import os

#ejoi-2019-1-UKR.pdf -> ejoi-2019-1-uk_UKR.pdf


def reformat():
    contest = 'ejoi'
    year = '2024'
    def make_error(text):
        print(text)
        assert False
    folder_dir = os.path.join(os.path.dirname(__file__), '../..')
    with open(os.path.join(folder_dir, '.github', 'scripts', '../data/languages.json'), 'r') as f:
        languages = json.load(f)
        country_to_language = {}
        for lang in languages:
            for country in languages[lang]:
                country_to_language[country] = lang
        print(country_to_language)
        year_path = os.path.join(folder_dir, 'statements', contest, year)
        problems = 0
        max_problem = 0
        print(year_path)
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
                print(name)
                if name[-4:] != '.pdf':
                    make_error('wrong format of filename ' + statement)
                if len(name) != 7:
                    continue
                country = name[:3]
                language = country_to_language[country]
                new_name = language + "_" + country + ".pdf"
                print(new_name)
                parts[3] = new_name
                new_file_name = "-".join(parts)
                print(new_file_name)
                print(problem_path)
                os.rename(os.path.join(problem_path, statement), os.path.join(problem_path, new_file_name))


reformat()
