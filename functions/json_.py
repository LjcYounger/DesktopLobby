from json import loads, dumps, JSONDecodeError

def load_json(path, encoding='UTF-8-sig', startWords=['#'], joinWord='', to_string=False, to_json=True):
     try:
          with open(path, 'r', encoding=encoding) as txt:
               content = joinWord.join([s for s in txt.readlines() if not any(s.startswith(startWord) for startWord in startWords)])
          if to_json:
               content = loads(content)
          if to_string:
               content=dumps(content)
          return content
     except (FileNotFoundError, JSONDecodeError):
          return {} if to_json else ""