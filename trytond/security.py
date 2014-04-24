#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from trytond.pool import Pool
from trytond.config import CONFIG
from trytond.transaction import Transaction
from trytond.exceptions import NotLogged


def _get_pool(dbname):
    database_list = Pool.database_list()
    pool = Pool(dbname)
    if not dbname in database_list:
        pool.init()
    return pool


def login(dbname, loginname, password, cache=True):
    with Transaction().start(dbname, 0) as transaction:
        pool = _get_pool(dbname)
        User = pool.get('res.user')
        user_id = User.get_login(loginname, password)
        transaction.cursor.commit()
    if user_id:
        if not cache:
            return user_id
        with Transaction().start(dbname, user_id) as transaction:
            Session = pool.get('ir.session')
            session, = Session.create([{}])
            transaction.cursor.commit()
            return user_id, session.key
    return False


def logout(dbname, user, session):
    with Transaction().start(dbname, 0) as transaction:
        pool = _get_pool(dbname)
        Session = pool.get('ir.session')
        session, = Session.search([
                ('key', '=', session),
                ])
        name = session.create_uid.login
        Session.delete([session])
        transaction.cursor.commit()
    return name


def check_super(passwd):
    if passwd == CONFIG['admin_passwd']:
        return True
    else:
        raise Exception('AccessDenied')


def check(dbname, user, session):
    if user == 0:
        raise Exception('AccessDenied')
    if not user:
        raise NotLogged()
    with Transaction().start(dbname, user) as transaction:
        pool = _get_pool(dbname)
        Session = pool.get('ir.session')
        try:
            if not Session.check(user, session):
                raise NotLogged()
            else:
                return user
        finally:
            transaction.cursor.commit()
