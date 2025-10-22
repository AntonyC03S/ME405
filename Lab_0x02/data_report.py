import csv
import os

file_path = "data"


with open(file_path, "r", encoding="utf-8") as infile:
    reader = csv.reader(infile)
    header = next(reader)



