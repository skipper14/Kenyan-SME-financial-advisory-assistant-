# inspect_record.py
# Look at one record before processing anything: a data engineer never
# works on a file they have not opened.
import json

records = json.load(open("operational_data.json"))
first = records[0]

print("QUESTION:", first["question"])
print()
print("ANSWER:  ", first["answer"])