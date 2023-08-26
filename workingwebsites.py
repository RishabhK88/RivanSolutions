import csv

l1=[]

with open('feat.csv', 'r', encoding="utf-8") as read_obj:
    csv_reader = csv.reader(read_obj)
    for i, row in enumerate(csv_reader):
        if len(row[1])>15:
            l1.append(row[0])
            
print(len(l1))

with open('working.csv', 'w+', encoding="utf-8") as fp:
    for i in l1:
        fp.write(i+'\n')