import pymysql


class DBConnet(object):
    def __init__(self):
        """
        初始化 mysql 数据库连接
        """
        self.conn = pymysql.connect(
        host='192.168.102.242'
        ,port=3306
        ,user="root"
        ,passwd="admin@aq123"
        ,db='mnvc_bak')

        self.cur = self.conn.cursor()

    def selectUrlfunc(self):
        """
        从 urllist 表中读取出需下载信息的 id 号和数据源网页地址
        """
        try:
            self.cur.execute("select id,url from urllist;")
            result = self.cur.fetchall()
            return result
        except Exception as e:
            print(str(e))

    def selectTagfunc(self):
        """
        从 taglist 表中取得需下载信息 id 所对应的 html 元素
        """
        try:
            self.cur.execute("select * from taglist;")
            result = self.cur.fetchall()
            return result
        except Exception as e:
            print(str(e))
  
    def selectTablefunc(self):
        """
        从 urllist 表中读取出需下载信息的 id 号和存放的数据表名
        """
        try:
            self.cur.execute("select id,table_name from urllist;")
            result = self.cur.fetchall()
            return result
        except Exception as e:
            print(str(e))
            
    def execfunc(self, table_name, path, id):
        """
        提交数据内容 id 、存放的数据表名称和在磁盘上的物理路径
        执行数据库插入
        """
        sql = 'insert into ' + table_name + '(path,id) values ("' + path +'","'+ id + '");'
        print(sql)
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except Exception as e:
            print(str(e))
