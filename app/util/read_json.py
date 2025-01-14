import json



def read_json(file_path):
    #fakeids = []
    with open(file_path, mode='r', encoding='utf-8') as file:
    #     data = json.load(file)
    #     for entry in data:
    #         fakeids.append(entry["fakeid"])
    # return fakeids
        return json.load(file)

