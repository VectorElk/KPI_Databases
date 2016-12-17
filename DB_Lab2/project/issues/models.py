from django.utils import timezone

import MySQLdb
from django.conf import settings

db_conf = settings.DATABASES['default']
db = MySQLdb.connect(
    host=db_conf['HOST'],
    user=db_conf['USER'],
    passwd=db_conf['PASSWORD'],
    db=db_conf['NAME']
)

# or we can use
# from django.db import connection as db
# and cursor.lastrowid instead of db.insert_id()

class Issue:
    _select_query = (
        "SELECT  `issues`.`id`, `title`, `description`, `issues`.`create_time`,"
        "`update_time`,"

        "`priority_id`, `priority`.`text`, `priority`.`priority_value`,"

        "`status_id`, `status`.`text`, `status`.`icon`,"

        "`created_by_user_id`, `c_u`.`username`, `c_u`.`email`, `c_u`.`password`,"
        "`c_u`.`create_time`, `c_u`.`is_blocked`, "

        "`assigned_to_user_id`, `a_u`.`username`, `a_u`.`email`, `a_u`.`password`,"
        "`a_u`.`create_time`, `a_u`.`is_blocked` "

        "FROM `issues_issues` `issues` "
        "JOIN `issues_users` `c_u` ON `created_by_user_id` = `c_u`.`id` "
        "LEFT JOIN `issues_users` `a_u` ON `assigned_to_user_id` = `a_u`.`id` "
        "JOIN `issues_issue_status` `status` ON `status_id` = `status`.`id` "
        "JOIN `issues_issue_priority` `priority` ON `priority_id` = `priority`.`id`")

    def __init__(self, title, description, create_time, priority, status, created_by, assigned_to):
        self._id = None
        self._title = title
        self._description = description
        self._create_time = create_time
        self._priority = priority
        self._status = status
        self._created_by = created_by
        self._assigned_to = assigned_to
        self._update_time = None
        self._changes = {}

    @property
    def id(self):
        return self._id

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        if self._title == value:
            return
        self._title = value
        self._changes['title'] = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        if self._description == value:
            return
        self._description = value
        self._changes['description'] = value

    @property
    def create_time(self):
        return self._create_time

    @property
    def priority(self):
        return self._priority

    @priority.setter
    def priority(self, value):
        if self._priority == value:
            return
        self._priority = value
        self._changes['priority_id'] = value.id if value else None

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if self._status == value:
            return
        self._status = value
        self._changes['status_id'] = value.id if value else None

    @property
    def created_by(self):
        return self._created_by

    @property
    def assigned_to(self):
        return self._assigned_to

    @assigned_to.setter
    def assigned_to(self, value):
        if self._assigned_to == value:
            return
        self._assigned_to = value
        self._changes['assigned_to_user_id'] = value.id if value else None

    @property
    def update_time(self):
        return self._update_time

    @update_time.setter
    def update_time(self, value):
        if self._update_time == value:
            return
        self._update_time = value
        self._changes['update_time'] = timezone.make_naive(value, timezone.utc)

    @staticmethod
    def get_all():
        c = db.cursor()
        c.execute(Issue._select_query)
        issues = []
        while True:
            e = c.fetchone()
            if not e:
                break
            i = Issue.from_query_result(e)
            issues.append(i)
        return issues

    @staticmethod
    def get_filtered(min_date=None, max_date=None, reporter_is_blocked=None, keywords=None):
        c = db.cursor()
        query = Issue._select_query
        filter = []
        filter_args = []
        if min_date:
            filter.append('`issues`.`create_time` >= TIMESTAMP(%s)')
            filter_args.append(timezone.make_naive(min_date, timezone.utc))
        if max_date:
            filter.append('`issues`.`create_time` <= TIMESTAMP(%s)')
            filter_args.append(timezone.make_naive(max_date, timezone.utc))
        if reporter_is_blocked is not None:
            filter.append('`c_u`.`is_blocked` = %s')
            filter_args.append(int(reporter_is_blocked))
        if keywords:
            filter.append('MATCH (`title`, `description`) AGAINST (%s IN BOOLEAN MODE)')
            filter_args.append(keywords)
        if filter:
            query += ' WHERE ' + ' AND '.join(filter)
        c.execute(query, filter_args)
        issues = []
        while True:
            e = c.fetchone()
            if not e:
                break
            i = Issue.from_query_result(e)
            issues.append(i)
        return issues

    @staticmethod
    def get_by_id(id):
        c = db.cursor()
        query = Issue._select_query + ' WHERE `issues`.`id` = %s'
        c.execute(query, (id,))
        entry = c.fetchone()
        return Issue.from_query_result(entry) if entry else None

    @staticmethod
    def from_query_result(data):
        i = Issue(*data[1:3],
                  timezone.make_aware(data[3], timezone.utc),
                  priority=IssuePriority.from_query_result(data[5:8]),
                  status=IssueStatus.from_query_result(data[8:11]),
                  created_by=User.from_query_result(data[11:17]),
                  assigned_to=User.from_query_result(data[17:]) if data[17] else None)
        i._id = data[0]
        i._update_time = timezone.make_aware(data[4], timezone.utc) if data[4] else None
        return i

    @staticmethod
    def delete(id=None):
        c = db.cursor()
        query = "DELETE FROM `issues_issues`"
        args = None
        if id:
            args = (int(id),)
            query += ' WHERE `id` = %s'
        c.execute(query, args)
        c.close()
        db.commit()

    def save(self):
        if not self._id:
            query = ('INSERT INTO `issues_issues` ('
                     '`title`, `description`, `create_time`, `update_time`, '
                     '`assigned_to_user_id`, `created_by_user_id`, `priority_id`, `status_id`) '
                     'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)')
            args = (
                self._title,
                self._description,
                timezone.make_naive(self._create_time, timezone.utc),
                timezone.make_naive(self._update_time, timezone.utc) if self._update_time else None,
                self._assigned_to.id if self._assigned_to else None,
                self._created_by.id,
                self._priority.id,
                self._status.id
            )
        elif not self._changes:
            return
        else:
            query = 'UPDATE `issues_issues` SET `{}` = %s WHERE `id` = %s'.format(
                '` = %s, `'.join(self._changes.keys())
            )
            args = tuple(self._changes.values()) + (self.id,)
            self._changes.clear()

        c = db.cursor()
        c.execute(query, args)
        c.close()
        if not self._id:
            self._id = db.insert_id()
        db.commit()

    def __str__(self):
        return self.title

    def __eq__(self, other):
        return other and other.id and self.id == other.id


class User:
    _select_query = ("SELECT `id`, `username`, `email`, `password`, `create_time`, `is_blocked`"
                     " FROM `issues_users`")

    def __init__(self, username, email, password, create_time, is_blocked):
        self.id = None
        self.username = username
        self.email = email
        self.password = password
        self.create_time = create_time
        self.is_blocked = bool(is_blocked)

    def save(self):
        pass

    def __str__(self):
        return self.username

    def __eq__(self, other):
        return other and self.id == other.id

    @staticmethod
    def get_all():
        c = db.cursor()
        c.execute(User._select_query)
        users = []
        while True:
            e = c.fetchone()
            if not e:
                break
            users.append(User.from_query_result(e))
        c.close()
        return users

    @staticmethod
    def get_by_id(id):
        c = db.cursor()
        query = User._select_query + ' WHERE `id` = %s'
        c.execute(query, (id,))
        entry = c.fetchone()
        c.close()
        return User.from_query_result(entry) if entry else None

    @staticmethod
    def get_choices(allow_empty=True):
        def real_get():
            c = db.cursor()
            query = "SELECT `id`, `username` FROM `issues_users`"
            c.execute(query)
            users = [(None, '')] if allow_empty else []
            while True:
                e = c.fetchone()
                if not e:
                    break
                users.append(e)
            c.close()
            return users
        return real_get

    @staticmethod
    def from_query_result(data):
        u = User(*data[1:])
        u.id = data[0]
        return u

    @staticmethod
    def bulk_create(entries):
        c = db.cursor()
        query = ("INSERT INTO `issues_users` "
                 "(`username`, `email`, `password`, `create_time`, `is_blocked`)"
                 "VALUES (%s, %s, %s, %s, %s);")
        c.executemany(
            query,
            [(e.username, e.email, e.password, e.create_time, e.is_blocked) for e in entries]
        )
        c.close()
        db.commit()

    @staticmethod
    def delete():
        c = db.cursor()
        query = "DELETE FROM `issues_users`"
        c.execute(query)
        c.close()
        db.commit()


class IssuePriority:
    _select_query = "SELECT `id`, `text`, `priority_value` FROM `issues_issue_priority`"

    def __init__(self, text, priority_value):
        self.id = None
        self.text = text
        self.priority_value = priority_value

    def save(self):
        pass

    def __str__(self):
        return self.text

    def __eq__(self, other):
        return other and self.id == other.id

    @staticmethod
    def get_all():
        c = db.cursor()
        c.execute(IssuePriority._select_query)
        prorities = []
        while True:
            e = c.fetchone()
            if not e:
                break
            prorities.append(IssuePriority.from_query_result(e))
        return prorities

    @staticmethod
    def get_by_id(id):
        c = db.cursor()
        query = IssuePriority._select_query + ' WHERE `id` = %s'
        c.execute(query, (id,))
        entry = c.fetchone()
        return IssuePriority.from_query_result(entry) if entry else None

    @staticmethod
    def get_choices():
        c = db.cursor()
        c.execute("SELECT `id`, `text` FROM `issues_issue_priority` ORDER BY `priority_value`")
        prorities = []
        while True:
            e = c.fetchone()
            if not e:
                break
            prorities.append(e)
        return prorities

    @staticmethod
    def from_query_result(data):
        u = IssuePriority(*data[1:])
        u.id = data[0]
        return u

    @staticmethod
    def bulk_create(entries):
        c = db.cursor()
        query = ("INSERT INTO `issues_issue_priority` (`priority_value`, `text`)"
                 "VALUES (%s, %s);")
        c.executemany(query, [(e.priority_value, e.text) for e in entries])
        c.close()
        db.commit()

    @staticmethod
    def delete():
        c = db.cursor()
        query = "DELETE FROM `issues_issue_priority`"
        c.execute(query)
        c.close()
        db.commit()


class IssueStatus:
    _select_query = "SELECT `id`, `text`, `icon` FROM `issues_issue_status`"

    def __init__(self, text, icon):
        self.id = None
        self.text = text
        self.icon = icon

    def save(self):
        pass

    def __eq__(self, other):
        return other and self.id == other.id

    @staticmethod
    def get_all():
        c = db.cursor()
        c.execute(IssueStatus._select_query)
        statuses = []
        while True:
            e = c.fetchone()
            if not e:
                break
            statuses.append(IssueStatus.from_query_result(e))
        return statuses

    @staticmethod
    def get_by_id(id):
        c = db.cursor()
        query = IssueStatus._select_query + ' WHERE `id` = %s'
        c.execute(query, (id,))
        entry = c.fetchone()
        return IssueStatus.from_query_result(entry) if entry else None

    @staticmethod
    def get_choices():
        c = db.cursor()
        c.execute(IssueStatus._select_query)
        statuses = []
        while True:
            e = c.fetchone()
            if not e:
                break
            statuses.append(e[:-1])
        return statuses

    @staticmethod
    def from_query_result(data):
        u = IssueStatus(*data[1:])
        u.id = data[0]
        return u

    @staticmethod
    def bulk_create(entries):
        c = db.cursor()
        query = ("INSERT INTO `issues_issue_status` (`text`, `icon`)"
                 "VALUES (%s, %s);")
        c.executemany(query, [(e.text, e.icon) for e in entries])
        c.close()
        db.commit()

    @staticmethod
    def delete():
        c = db.cursor()
        query = "DELETE FROM `issues_issue_status`"
        c.execute(query)
        c.close()
        db.commit()
