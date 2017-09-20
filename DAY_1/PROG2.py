
f = open('workfile', 'r+')
f.write('python with json')
f.readline(1)
f.seek(8)
f.read(1)
f.seek(-3, 2)
f.read(1)
f.close()
with open('workfile', 'r') as f:
    read_data = f.read()
    f.closed


import json

x = json.load(f)
json.dump(x, f)

student = {"101": {"class": 'IV', "Name": 'Rohit', "Roll_no": 7},
           "102": {"class": 'IV', "Name": 'David', "Roll_no": 8},
           "103": {"class": 'IV', "Name": 'Samiya', "Roll_no": 12}}
# print(json.dumps(student))
# print(json.dumps(student, sort_keys = True))
tuple1 = (1, 2, 3, 4, 5)
# print(json.dumps(tuple1))
string1 = 'Python with JSON'
# print(json.dumps(string1))
list1 = ["a", "b", "c"]
# print(json.dumps(list1))


json_data = '{"103": {"class": "V", "Name": "Samiya", "Roll_n": 12}, "102": {"class": "V", "Name": "David", "Roll_no": 8}, "101": {"class": "V", "Name": "Rohit", "Roll_no": 7}}'
jsonToPython = (json.loads(json_data))
# print jsonToPython

# print jsonToPython["103"]


pythonDictionary = {'name': 'Bob', 'age': 44, 'isEmployed': True}

dictionaryToJson = json.dumps(pythonDictionary)

# print dictionaryToJson
