from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.code import Code


class DB(object):
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.test

    def getJournalList(self):
        journals = [journal for journal in self.db.journal.find()]
        return journals

    def getStudentList(self):
        students = [student for student in self.db.student.find()]
        return students

    def getTeacherList(self):
        teachers = [teacher for teacher in self.db.teacher.find()]
        return teachers

    def getGroupList(self):
        groups = [group for group in self.db.group.find()]
        return groups

    def getSubjectList(self):
        subjects = [subject for subject in self.db.subject.find()]
        return subjects

    def removeJournal(self, id):
        self.db.journal.delete_one({'journal_id': ObjectId(id)})

    def saveJournal(self, info):
        mark_letter = self.db.journal.find_one({'journal_id': ObjectId(info['mark_letter'])})
        mark_numeric = self.db.journal.find_one({'journal_id': ObjectId(info['mark_numeric'])})
        group_id = self.db.group.find_one({'journal_id': ObjectId(info['group_id'])})
        teacher_id = self.db.teacher.find_one({'journal_id': ObjectId(info['teacher_id'])})
        subject_id = self.db.subject.find_one({'journal_id': ObjectId(info['subject_id'])})
        student_id = self.db.student.find_one({'journal_id': ObjectId(info['student_id'])})
        order = {'mark_letter': mark_letter, 'mark_numeric': mark_numeric, 'group_id': group_id,
                 'teacher_id': teacher_id, 'subject_id': subject_id, 'student_id': student_id}
        self.db.journal.insert(order)

    def updateJournal(self, info):
        mark_letter = self.db.journal.find_one({'_id': ObjectId(info['mark_letter'])})
        mark_numeric = self.db.journal.find_one({'_id': ObjectId(info['mark_numeric'])})
        group_id = self.db.group.find_one({'_id': ObjectId(info['group_id'])})
        teacher_id = self.db.teacher.find_one({'_id': ObjectId(info['teacher_id'])})
        subject_id = self.db.subject.find_one({'_id': ObjectId(info['subject_id'])})
        student_id = self.db.student.find_one({'_id': ObjectId(info['student_id'])})
        journal = {'mark_letter': mark_letter, 'mark_numeric': mark_numeric, 'group_id': group_id,
                   'teacher_id': teacher_id, 'subject_id': subject_id, 'student_id': student_id}
        self.db.journal.update_one({'_id': ObjectId(info['journal'])}, {'$set': journal})

    def getTopStudentsAggregate(self):
        students = list(self.db.journal.aggregate(
            [{"$unwind": "student_id.student_name"},
             {"$project": {"student_name": "student_id.student_name", "count": {"$add": [1]}}},
             {"$group": {"student_id": "student_name", "number": {"$sum": "$count"}}},
             {"$sort": {"number": -1}}, {"$limit": 3}]))
        return students

    def mapMostMarks(self):
        mapper = Code("""
                            function() {
                                   var key = this.student_id.student_name;
                                   var value = {count : 1};
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
        result = self.db.journal.map_reduce(mapper, reducer, "result")
        res = list(result.find())
        print(res)

    def mapTopStudents(self):
        mapper = Code("""
                    function() {
                           var key = this.student_id.student_name;
                           var value = {

                           }
                           emit(key, value);
                    };
                    """)
        reducer = Code("""
                        function (key, values) {

                            var count = 0;
                            for(var i in values){
                                count += values[i].count;
                                total += values[i].total;
                            }
                            return {total: total, count: count};
                        };
                        """)
        result = self.db.order.map_reduce(mapper, reducer, "result")
        res = list(result.find())
        print(res[0]['value']['total'] / res[0]['value']['count'])