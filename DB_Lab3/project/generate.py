import math
import random
import time

from pymongo import MongoClient


def get_mark_letter(mark):
    if mark > 94:
        return 'A'
    if mark > 84:
        return 'B'
    if mark > 74:
        return 'C'
    if mark > 64:
        return 'D'
    if mark > 59:
        return 'E'
    return 'F'

client = MongoClient()
db = client.db_lab2

student = list(db.student.find())
teacher = list(db.teacher.find())
subject = list(db.subject.find())
group = list(db.group.find())

start_time = time.time()

for i in range(0, 100000):
    mark_numeric = random.randrange(40, 100, 1)
    journal = {
        'student_id': random.choice(student),
        'teacher_id': random.choice(teacher),
        'subject_id': random.choice(subject),
        'group_id': random.choice(group),
        'mark_numeric': mark_numeric,
        'mark_letter': get_mark_letter(mark_numeric)
    }
    db.journal_redis.insert(journal)

elapsed_time = time.time() - start_time
print(elapsed_time)