from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.code import Code
import redis
import pickle


class DB(object):
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.db_lab2
        self.r = redis.StrictRedis()

    def getJournal(self, id_):
        return self.db.journal_redis.find_one(filter={'_id': ObjectId(id_)})

    def getJournalList(self, offset=0, limit=10):
        journals = self.db.journal_redis.find(skip=offset, limit=limit)
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
        self.db.journal_redis.delete_one({'_id': ObjectId(id)})
        self.r.incr('version')

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
        self.db.journal_redis.insert_one(journal)
        self.r.incr('version')

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
        self.db.journal_redis.update_one({'_id': ObjectId(info['journal'])}, {'$set': journal})
        self.r.incr('version')

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
        result = self.db.journal_redis.map_reduce(mapper, reducer, "result")
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
        result = self.db.journal_redis.map_reduce(mapper, reducer, "result")
        res = list(result.find())
        return res

    def mapByMark(self, mark_min, mark_max):
        mapper = Code('''
            function(){
                var k = {
                    mark_numeric: this.mark_numeric,
                    student: this.student_id.student_name
                }
                emit(k, 1);
            }
        ''')
        reducer = Code('''
            function(key, values) {
                return Array.sum(values);
            }
        ''')
        results = self.db.journal_redis.map_reduce(
            mapper, reducer, {'inline': 1},
            query={'mark_numeric': {'$gte': mark_min-1, '$lt': mark_max}}
        )['results']
        d = dict()
        for r in results:
            s = d.setdefault(r['_id']['student'], dict())
            s[r['_id']['mark_numeric'] + 1] = r['value']
        return d

    def sort(self, request):
        req = str(request).partition('&')[2]
        if self.r.exists(req) != 0 and self.r.hget(req, 'version') == self.r.get('version'):
            journal = pickle.loads(self.r.hget(req, 'res'))
        else:
            query = {}
            if request.GET['fromMark'] != '' or request.GET['toMark'] != '':
                query["total"] = {}
                if request.GET['fromMark'] != '':
                    query["total"]['$gte'] = int(request.GET['fromMark'])
                if request.GET['toMark'] != '':
                    query["total"]['$lte'] = int(request.GET['toMark'])
            if request.GET['student_id'] != '0':
                query["student_id._id"] = ObjectId(request.GET['student_id'])
            journal = list(self.db.journal_redis.find(query))
            self.r.hmset(req, {'res': pickle.dumps(journal), 'version': self.r.get('version')})
        return list(journal)
