from datetime import datetime
import random
import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker


class PostgresDB:
    """
    db = PostgresDB("postgresql+psycopg2://googl:googl@38.34.175.87:9888/googl")
    """

    def __init__(self, db_uri):
        self.engine = create_engine(db_uri, echo=True)
        self.session = scoped_session(sessionmaker(bind=self.engine))
        self.have_remote_task_user = {}

    def createTable(self, table_name, sql):
        """新建表"""
        try:
            with self.session.begin():
                self.session.execute(text(sql))
            info = f"创建表《{table_name.lower()}》成功"
            return True, info
        except Exception as e:
            info = f"创建表《{table_name.lower()}》失败 报错：{e}"
            return False, info

    def createUserTable(self):
        """创建用户表"""
        table_name = "users"
        sql = f"""
            CREATE TABLE {table_name.lower()} (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                pwd VARCHAR(100) NOT NULL,
                points INT NOT NULL,
                freeze_points INT NOT NULL,
                wait_points INT NOT NULL,
                login_time VARCHAR(100)
            )"""
        return self.createTable(table_name, sql)

    def createLogTable(self, account):
        """创建任务日志表"""
        table_name = "log_" + account.replace('@', '__').replace(
            '-', '___').replace('.', '_')
        sql = f"""
            CREATE TABLE {table_name.lower()} (
                id SERIAL PRIMARY KEY,
                task_id VARCHAR(100) NOT NULL,
                title VARCHAR(100) NOT NULL,
                task_type VARCHAR(100) NOT NULL,
                start_time INT NOT NULL
            )"""
        return self.createTable(table_name, sql)

    def get24LogJson(self, account):
        """获取24小时内任务发送数 获取24小时内不同 task_type 的数据数量"""
        table_name = "log_" + account.replace('@', '__').replace(
            '-', '___').replace('.', '_')
        try:
            with self.session.begin():
                sql = text(
                    f"""SELECT task_type, COUNT(*) AS count FROM {table_name} WHERE TO_TIMESTAMP(start_time) > (NOW() - INTERVAL '24 hour') GROUP BY task_type"""
                )
                results = self.session.execute(sql).fetchall()
            log_json = {}
            for task_type, count in results:
                log_json[task_type] = count
            print(log_json)
            self.deleteOldLogs(account)
            return True, log_json
        except Exception as e:
            info = f"获取24小时内任务日志时出错：{e}"
            return False, info

    def deleteOldLogs(self, account):
        """删除超过24小时的任务日志数据"""
        table_name = "log_" + account.replace('@', '__').replace(
            '-', '___').replace('.', '_')
        try:
            with self.session.begin():
                sql = text(
                    f"""DELETE FROM {table_name} WHERE TO_TIMESTAMP(start_time) < NOW() - INTERVAL '24 hour'"""
                )
                self.session.execute(sql)
            return True, "删除成功"
        except Exception as e:
            info = f"删除超过24小时的任务日志数据时出错：{e}"
            return False, info

    def insertLogData(self, account, task_log_sql_data):
        """添加任务日志"""
        task_log_table_name = "log_" + account.replace('@', '__').replace(
            '-', '___').replace('.', '_')
        try:
            with self.session.begin():
                task_log_sql = text(f"""
                INSERT INTO {task_log_table_name.lower()} (task_id, title, task_type, start_time)
                VALUES (:task_id, :title, :task_type, :start_time)
                """)
                self.session.execute(task_log_sql,
                                     task_log_sql_data)  # 插入任务日志数据
        except Exception as e:
            info = f"《{task_log_table_name.lower()}》插入任务日志数据 失败 报错：{e}"
            print(info)
            if "does not exist" in str(e):
                self.createLogTable(account)
                self.insertLogData(account, task_log_sql_data)

    def updatePoints(self, username, freeze_points_delta, points_delta):
        """更新用户的冻结积分和总积分"""
        try:
            with self.session.begin():
                self.session.execute(
                    text(
                        """UPDATE users SET freeze_points = freeze_points + :freeze_points_delta, points = points + :points_delta WHERE username = :username"""
                    ),
                    {
                        "username": username,
                        "freeze_points_delta": freeze_points_delta,
                        "points_delta": points_delta,
                    },
                )
                info = f"[{username}] 更新用户积分 成功"
                return True, info
        except Exception as e:
            info = f"更新用户积分时出错：{e}"
            return False, info

    def createTaskTable(self, user):
        """创建任务数据表"""
        table_name = f"task_{user}"
        sql = f"""
            CREATE TABLE {table_name.lower()} (
                id SERIAL PRIMARY KEY,
                task_name VARCHAR(100) NOT NULL,
                title VARCHAR(100) NOT NULL,
                start_time VARCHAR(100),
                do_user VARCHAR(100),
                do_account VARCHAR(100),
                finish_time VARCHAR(100),
                link VARCHAR(150) NOT NULL,
                task_type VARCHAR(100) NOT NULL,
                task_data TEXT NOT NULL,
                publish_time VARCHAR(100) NOT NULL,
                is_remote BOOLEAN NOT NULL,
                life INT NOT NULL
            )"""
        return self.createTable(table_name, sql)

    def getUserTaskData(self,
                        user,
                        count,
                        do_user,
                        do_account,
                        limit_list=None):
        """获取用户任务 （start_time为空的最小id的数据）"""
        if user is None:
            if len(self.have_remote_task_user) == 0:
                # 更新一下远程任务用户库
                task_users = [
                    i for i in self.getAllTables() if i.startswith('task_')
                ]
                with self.session.begin():
                    for task_user in task_users:
                        user_name = task_user[5:]
                        sql = text(
                            f"SELECT task_type, COUNT(*) FROM {task_user} WHERE is_remote = True GROUP BY task_type"
                        )
                        querry_result = self.session.execute(sql).fetchall()
                        if len(querry_result) > 0:
                            print(task_user, '存在远程任务', querry_result)
                            have_task_dict = {}
                            for k, v in querry_result:
                                have_task_dict[k] = v
                            self.have_remote_task_user[
                                user_name] = have_task_dict
                        else:
                            print(task_user, '不存在远程任务')
            if len(self.have_remote_task_user) == 0:
                # 更新后还是没有远程任务
                info = "当前无可执行远程任务"
                print(info)
                return False, info
            if limit_list is None:
                remote_user = random.choice(
                    list(self.have_remote_task_user.keys()))
                have_task_dict = self.have_remote_task_user.pop(
                    remote_user)  # 删除
            else:
                for remote_user, tt in self.have_remote_task_user.items():
                    if len(set(tt.keys()) - set(limit_list)) > 0:
                        have_task_dict = self.have_remote_task_user.pop(
                            remote_user)  # 删除
                        break
                else:
                    # 没有符合的任务
                    info = f"当前无可执行远程任务 [排除任务：{','.join(limit_list)}]"
                    print(info)
                    return False, info
            user = remote_user
        table_name = f"task_{user}"
        try:
            task_log_sql_datas = []
            with self.session.begin():
                if limit_list is None:
                    sql = text(
                        f"SELECT * FROM {table_name.lower()} WHERE start_time = '' ORDER BY RANDOM() LIMIT {count}"
                    )
                else:
                    limit_list_to_text = "'" + "', '".join(limit_list) + "'"
                    sql = text(
                        f"SELECT * FROM {table_name.lower()} WHERE start_time = '' AND task_type NOT IN ({limit_list_to_text}) ORDER BY RANDOM() LIMIT {count}"
                    )
                results = self.session.execute(sql).fetchall()
                datas = []
                print(results)
                for result in results:
                    task_data = {
                        'user': user,
                        'id': result[0],
                        'type': result[8],
                        'data': result[9]
                    }
                    print(
                        f"{do_user} 获取用户{user}的id:{task_data['id']} {task_data['type']} 任务"
                    )
                    datas.append(task_data)
                    # 更新任务信息
                    task_info_sql_data = {
                        'start_time':
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'do_user': do_user,
                        'do_account': do_account,
                        'id': result[0]
                    }
                    task_info_sql = text(
                        f"UPDATE {table_name.lower()} SET start_time = :start_time, do_user = :do_user, do_account = :do_account WHERE id = :id"
                    )
                    self.session.execute(task_info_sql, task_info_sql_data)
                    # 准备任务日志数据
                    task_log_sql_data = {
                        "task_id": f"{user}-{result[0]}",
                        "title": result[2],
                        "task_type": result[8],
                        "start_time": int(time.time()),
                    }
                    task_log_sql_datas.append(task_log_sql_data)
            if len(datas) > 0:
                # 添加任务日志
                for task_log_sql_data in task_log_sql_datas:
                    self.insertLogData(do_account, task_log_sql_data)
                return True, datas
            else:
                info = f"用户'{user}' 无可执行任务 [排除任务：{','.join(limit_list)}]"
                return False, info
        except Exception as e:
            info = f"获取用户任务时出错：{e}"
            print(info)
            return False, info

    def fetchData(self, table_name):
        """获取表格中所有数据"""
        with self.session.begin():
            result = self.session.execute(
                text(f"SELECT * FROM {table_name.lower()}"))
            return result.fetchall()

    def updateFinishTaskData(self, user, data):
        """更新完成任务数据"""
        table_name = f"task_{user}"
        try:
            with self.session.begin():
                sql = text(
                    f"UPDATE {table_name.lower()} SET finish_time = :finish_time, link = :link WHERE id = :id"
                )
                self.session.execute(sql, data)
                info = f"《{table_name.lower()}》更新任务完成数据 成功"
                return True, info
        except Exception as e:
            info = f"《{table_name.lower()}更新任务完成数据 失败 报错：{e}"
            print(info)
            return False, info

    def insertTaskData(self, user, data):
        """插入任务数据"""
        table_name = f"task_{user}"
        try:
            with self.session.begin():
                sql_query = text(f"""
                    INSERT INTO {table_name.lower()} (task_name, title, start_time, do_user, do_account, finish_time, 
                    link, task_type, task_data, publish_time, is_remote, life) 
                    VALUES (:task_name, :title, :start_time, :do_user, :do_account, :finish_time, 
                    :link, :task_type, :task_data, :publish_time, :is_remote, :life) 
                    """)
                self.session.execute(sql_query, data)
                data = {
                    "username": user,
                    "freeze_points_delta": 10,
                    "points_delta": -10,
                }
                sql_text = text(
                    """UPDATE users SET freeze_points = freeze_points + :freeze_points_delta, points = points + :points_delta WHERE username = :username"""
                )
                self.session.execute(sql_text, data)
            info = f"《{table_name.lower()}》插入任务数据 成功"
            return True, info
        except Exception as e:
            info = f"《{table_name.lower()}》插入任务数据 失败 报错：{e}"
            print(info)
            if "does not exist" in str(e):
                # print('不存在则创建')
                self.createTaskTable(user)
                return self.insertTaskData(user, data)
            return False, info

    def insertUserData(self, data):
        """插入用户数据"""
        table_name = "users"
        try:
            with self.session.begin():
                sql_query = text(f"""
                    INSERT INTO {table_name.lower()} (username, pwd, points, freeze_points, wait_points, login_time)
                    VALUES (:username, :pwd, :points, :freeze_points, :wait_points, :login_time)
                    """)
                self.session.execute(sql_query, data)
            info = f"《{table_name.lower()}》插入用户'{data['username']}'数据 成功"
            return True, info
        except Exception as e:
            info = f"《{table_name.lower()}》插入用户'{data['username']}'数据 失败 报错：{e}"
            if "does not exist" in str(e):
                # print('不存在则创建')
                self.createUserTable()
                return self.insertUserData(data)
            return False, info

    def getUserDataByUsername(self, username):
        """通过用户名获取用户数据"""
        table_name = "users"
        try:
            with self.session.begin():
                result = self.session.execute(
                    text(
                        f"SELECT * FROM {table_name.lower()} WHERE username = :username"
                    ),
                    {
                        "username": username
                    },
                ).fetchone()
                if result:
                    print(result)
                    user_data = result[3:7]
                    # 如果找到匹配的用户数据，将结果转换为字典形式并返回
                    return True, user_data
                else:
                    info = f"用户名 '{username}' 不存在"
                    return False, info
        except Exception as e:
            info = f"查询用户数据时出错：{e}"
            return False, info

    def loginVerify(self, user, pwd):
        """登录验证"""
        table_name = "users"
        try:
            with self.session.begin():
                result = self.session.execute(
                    text(
                        f"SELECT * FROM {table_name.lower()} WHERE username = :username AND pwd = :pwd"
                    ),
                    {
                        "username": user,
                        "pwd": pwd
                    },
                )
                user_data = result.fetchone()
                if user_data:
                    info = "登录验证成功"
                    # 更新一下登录时间
                    sql_query = text(f"""
                    UPDATE {table_name.lower()} SET login_time = :new_login_time 
                    WHERE username = :username
                    """)
                    self.session.execute(
                        sql_query,
                        {
                            "new_login_time":
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "username":
                            user,
                        },
                    )
                    return True, info
                else:
                    info = "用户名或密码错误"
                    return False, info
        except Exception as e:
            info = f"登录验证失败 报错：{e}"
            return False, info

    def Scripts_insert_or_update_data(self, data):
        session = self.session()
        try:
            sql_query = text(
                "INSERT INTO Scripts (NAME, URL, COUNT_LIMIT) VALUES (:name, :url, :count_limit) ON CONFLICT (NAME) DO UPDATE SET URL = EXCLUDED.URL, COUNT_LIMIT = EXCLUDED.COUNT_LIMIT"
            )
            session.execute(sql_query, data)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    # Additional methods would be similarly updated...
    def getAllTables(self):
        """获取数据库中所有表名"""
        with self.session.begin():
            result = self.session.execute(
                text(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
                ))
            tables = [row[0] for row in result.fetchall()]
            return tables

    def dropAllTables(self):
        """删除数据库中所有表格"""
        with self.session.begin():
            result = self.session.execute(
                text(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
                ))
            tables = [row[0] for row in result.fetchall()]
            for table in tables:
                self.session.execute(text(f"DROP TABLE IF EXISTS {table}"))

    def dropTables(self, tables_to_drop):
        """删除指定的表格"""
        with self.session.begin():
            for table_name in tables_to_drop:
                self.session.execute(
                    text(f"DROP TABLE IF EXISTS {table_name.lower()}"))
                print(f'已删除表 {table_name.lower()}')


if __name__ == "__main__":
    # db = PostgresDB("postgresql+psycopg2://AdTools:AdTools@38.34.175.87:9888/AdTools")
    db = PostgresDB(
        "postgresql+psycopg2://adtools:adtools@38.34.175.87:9888/adtools")
    # ok,info = db.createTaskTable('se8888')
    # ok, info = db.createUserTable()
    # print(info)
    # print(db.getAllTables())
    # db.dropTables(['task_win88'])
    # r = db.getUserTaskData(None, 1, 'haha', 'seo888@gmx.com')
    # print(r)

    # r = db.get24LogJson('seo888@gmx.com')
    # data = {
    #     "task_name":'谷歌地图 20022222',
    #     "title":'欧洲杯买球网站3',
    #     "start_time":"2024-11-11",
    #     "do_user":'seo888',
    #     "do_account":'seo888@gmx.com',
    #     "finish_time":'',
    #     "link":'',
    #     "task_type":'谷歌地图',
    #     "task_data":'{"1":2}',
    #     "publish_time":f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    #     "is_remote":True,
    #     "life":15
    # }
    # datas = []
    # for i in range(10):
    #     new_data = data.copy()
    #     new_data['task_name'] = f'谷歌地图新{i+1}'
    #     datas.append(new_data)
    # print(db.insertTaskData('win88',datas))

    data = {
        "username": "kevin",
        "pwd": "168888",
        "points": 10000000,
        "freeze_points": 0,
        "wait_points": 0,
        "login_time": f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    }
    print(db.insertUserData(data))

    # r = db.fetchData('task_s88')
    # print(r)

    # db.dropAllTables()
    # print(db.getAllTables())
    # # # Example usage
    # # db.getColumns("Scripts")
    # data = {
    #     "name": "seo888@gmx.com4",
    #     "url": "http://api.seo888.cc/scripts/mapPush.py",
    #     "count_limit": 100,
    # }
    # db.Scripts_insert_or_update_data(data)
    # all_data = db.getAllData("Scripts")
    # print(all_data)
