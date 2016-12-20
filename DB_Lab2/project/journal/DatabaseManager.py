from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.code import Code


class DB(object):
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.db_lab2

    def getJournal(self, id_):
        return self.db.journals.find_one(filter={'_id': ObjectId(id_)})

    def getJournalList(self, offset=0, limit=10):
        journals = self.db.journals.find(skip=offset, limit=limit)
        return journals

    def getStudentList(self, allow_empty=True):
        students = [(None, '')] if allow_empty else []
        c = self.db.student.find(projection=['student_name'])
        students += [(s['_id'], s['student_name']) for s in c]
        return students

    def getTeacherList(self, allow_empty=True):
        teachers = [(None, '')] if allow_empty else []
        c = self.db.teacher.find(projection=['teacher_name'])
        teachers += [(s['_id'], s['teacher_name']) for s in c]
        return teachers

    def getGroupList(self, allow_empty=True):
        groups = [(None, '')] if allow_empty else []
        c = self.db.group.find(projection=['group_name'])
        groups += [(s['_id'], s['group_name']) for s in c]
        return groups

    def getSubjectList(self, allow_empty=True):
        subjects = [(None, '')] if      allow_empty else []
        c = self.db.subject.find(projection=['subject_name'])
        subjects += [(s['_id'], s['subject_name']) for s in c]
        return subjects

    def removeJournal(self, id):
        self.db.journals.delete_one({'_id': ObjectId(id)})

    def saveJournal(self, info):
        group_id = self.db.group.find_one(filter={'_id': ObjectId(info['group_id'])})
        teacher_id = self.db.teacher.find_one(filter={'_id': ObjectId(info['teacher_id'])})
        subject_id = self.db.subject.find_one(filter={'_id': ObjectId(info['subject_id'])})
        student_id = self.db.student.find_one(filter={'_id': ObjectId(info['student_id'])})
        journal = {'mark_letter': info['mark_letter'],
                   'mark_numeric': info['mark_numeric'],
                   'group_id': group_id,
                   'teacher_id': teacher_id,
                   'subject_id': subject_id,
                   'student_id': student_id}
        self.db.journals.insert_one(journal).inserted_id

    def updateJournal(self, info):
        group_id = self.db.group.find_one(filter={'_id': ObjectId(info['group_id'])})
        teacher_id = self.db.teacher.find_one(filter={'_id': ObjectId(info['teacher_id'])})
        subject_id = self.db.subject.find_one(filter={'_id': ObjectId(info['subject_id'])})
        student_id = self.db.student.find_one(filter={'_id': ObjectId(info['student_id'])})
        journal = {'mark_letter': info['mark_letter'],
                   'mark_numeric': info['mark_numeric'],
                   'group_id': group_id,
                   'teacher_id': teacher_id,
                   'subject_id': subject_id,
                   'student_id': student_id}
        self.db.journals.update_one({'_id': ObjectId(info['journal'])}, {'$set': journal})

    def getTopStudentsAggregate(self):
        students = list(self.db.journals.aggregate(
            [{"$project": {"name": "$student_id.student_name", "count": {"$add": ["$mark_numeric"]}}},
             {"$group": {"_id": "$name", "number": {"$sum": "$count"}}},
             {"$sort": {"number": -1}}]))
        return students

    def mapAvarageMarks(self):
        mapper = Code("""
                            function() {
                                       var key = this.student_id.student_name;
                                       var value = this.mark_numeric;
                                       emit(key, value);
                            };
                            """)
        reducer = Code("""
                                function (key, values) {
                                    return Array.avg(values);
                                };
                                """)
        result = self.db.journals.map_reduce(mapper, reducer, "result")
        res = list(result.find())
        return res

    def mapMostHighGrades(self):
        mapper = Code("""
                    function() {
                           var key = this.student_id.student_name;
                            var value = { count : 0 }
                            if (this.mark_letter == 'A'){
                                value = { count : 1 };
                            }
                            emit(key, value);
                    };
                    """)
        reducer = Code("""
                        function (key, values) {
                                    var count = 0;
                                    for(var i in values){
                                        count += values[i].count;
                                    }
                                    return {count: count};
                                };
                        """)
        result = self.db.journals.map_reduce(mapper, reducer, "result")
        res = list(result.find())
        return res