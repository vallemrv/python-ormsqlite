# @Author: Manuel Rodriguez <valle>
# @Date:   07-Sep-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 18-Sep-2017
# @License: Apache license vesion 2.0

import sqlite3

class Model(object):
    def __init__(self, table_name, db_name, **datos):
        self.lstCampos = []
        self.id = -1
        self.columns = "*"
        self.table_name = table_name
        self.db_name = db_name
        if 'pk' in datos:
            self.load_by_pk(datos['pk'])
        else:
            self.__cargarDatos__(**datos)


    def __cargarDatos__(self, **datos):
        for k, v in datos.items():
            if k=="id":
                self.id = v
            else:
                setattr(self, k, v)
                self.lstCampos.append(k)

    def __pack__(self, val):
        if type(val) in (str, unicode):
            return u'\"{0}\"'.format(unicode(val))
        else:
            return str(val)

    def __getenerate_joins__(self, joins):
        strJoins = []
        for j in joins:
            sql = j if j.startswith("INNER") else "INNER JOIN "+j
            strJoins.append(sql)

        return "" if len(strJoins) <=0 else ", ".join(strJoins)



    def delete(self):
        self.id = -1 if self.id == None else self.id
        sql = u"DELETE FROM {0} WHERE id={1};".format(self.table_name,
                                                      self.id)
        self.execute(sql)
        self.id = -1


    def getAll(self, **condition):
        self.tipo_relation = None if not "tipo_relation" in condition else condition['tipo_relation']
        self.id_tabla_nexo = -1 if not "id_tabla_nexo" in condition else condition['id_tabla_nexo']
        self.tabla_nexo = None if not "tabla_nexo" in condition else condition['tabla_nexo']
        order = "" if not 'order' in condition else "ORDER BY %s" % unicode(condition.get('order'))
        query = "" if not 'query' in condition else "WHERE %s" % unicode(condition.get("query"))
        limit = "" if not 'limit' in condition else "LIMIT %s" % condition.get("limit")
        offset = "" if not 'offset' in condition else "OFFSET %s" % condition.get('offset')
        self.columns = "*" if not 'columns' in condition else ", ".join(condition.get("columns"))
        joins = "" if not 'joins' in condition else self.__getenerate_joins__(condition.get("joins"))
        group = "" if not 'group' in condition else "GROUP BY %s" % condition.get("group")
        sql = u"SELECT {0} FROM {1} {2} {3} {4} {5} {6} {7};".format(self.columns, self.table_name,
                                                         joins, query, order, group, limit, offset)
        return self.select(sql)

    def select(self, sql):
        db = sqlite3.connect(self.db_name)
        cursor= db.cursor()
        cursor.execute(sql)
        reg = cursor.fetchall()
        d = cursor.description
        db.commit()
        db.close()
        registros = []

        for r in reg:
            res = dict({k[0]: v for k, v in list(zip(d, r))})
            obj = Model(table_name=self.table_name, db_name=self.db_name, **res)
            setattr(obj, 'tipo_relation', self.tipo_relation)
            setattr(obj, 'id_tabla_nexo', self.id_tabla_nexo)
            setattr(obj, 'tabla_nexo', self.tabla_nexo)

            registros.append(obj)

        return registros

    def execute(self, query):
        if sqlite3.complete_statement(query):
            db = sqlite3.connect(self.db_name)
            cursor= db.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.execute(query)
            db.commit()
            db.close()

    def load_first_by_query(self, **condition):
        reg = self.getAll(**condition)
        if len(reg) > 0:
            self.__cargarDatos__(**reg[0].toDICT())

    def load_by_pk(self, pk):
        sql = u"SELECT * FROM {0} WHERE ID={1};".format(self.table_name, pk)
        db = sqlite3.connect(self.db_name)
        cursor= db.cursor()
        cursor.execute(sql)
        reg = cursor.fetchone()
        d = cursor.description
        db.commit()
        db.close()
        if reg:
            res = dict({k[0]: v for k, v in list(zip(d, reg))})
            self.__cargarDatos__(**res)

    def toJSON(self):
        js = self.toDICT()
        return json.dumps(js, ensure_ascii=False)

    def toDICT(self):
        if self.id > 0:
            js = {"id": self.id}
        else:
            js = {}
        for key in self.lstCampos:
            v =  getattr(self, key)
            if self.columns == "*":
                if not (v == "None" or v is None):
                    js[key] = v
            elif key in self.columns and not (v == "None" or v is None):
                js[key] = v

        return js


    @staticmethod
    def exitsTable(db_name, table_name):
        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name='%s';"
        sql = sql % table_name
        db = sqlite3.connect(db_name)
        cursor= db.cursor()
        cursor.execute(sql)
        reg = cursor.fetchone()
        db.commit()
        db.close()
        return reg != None


    @staticmethod
    def add(db, sufix, parent, child):
        table_name_parent = parent.__class__.__name__.lower()
        table_name_child = child.__class__.__name__.lower()
        table_name = sufix+"_"+table_name_parent+"_"+table_name_child
        table_name_reverse = sufix+"_"+table_name_child+"_"+table_name_parent
        if Model.exitsTable(db, table_name):
            child.save()
            getattr(parent, table_name_child).add(child)
        elif Model.exitsTable(db, table_name_reverse):
            child.save()
            getattr(child, table_name_parent).add(parent)
        else:
            setattr(child, table_name_parent+"_id", parent.id)
            child.save()


    @staticmethod
    def get(db, sufix, parent, table_name_parent, table_name_child, **condition):
        table_name = sufix+"_"+table_name_parent+"_"+table_name_child
        if not Model.exitsTable(db, table_name):
            model = Model(db_name=db, table_name=sufix+"_"+table_name_child)
            query = ""
            if 'query' in condition:
                query = " AND "
            condition["query"] = query + table_name_parent+"_id="+str(parent.id)
            condition["tipo_relation"] = "foreingKey"
            return model.getAll(**condition)
        else:
            model = Model(db_name=db, table_name=sufix+"_"+table_name_child)
            condition["columns"] = [sufix+"_"+table_name_child+".*"]
            query = ""
            if 'query' in condition:
                query = " AND "
            condition["query"] = query + table_name_parent+"_id="+str(parent.id)
            on_join = u" ON {0}.{1}_id={2}.id".format(table_name, table_name_child, sufix+"_"+table_name_child)
            condition["joins"] = [table_name + on_join]
            condition["tipo_relation"] = "MANYTOMANY"
            condition["tabla_nexo"] = table_name
            condition["id_tabla_nexo"] = table_name_parent+"_id="+str(parent.id)+" AND "+table_name_child+"_id"
            return model.getAll(**condition)

    @staticmethod
    def toArrayDict(childs):
        lista = []
        for r in childs:
            reg = r.toDICT()
            lista.append(reg)

        return lista

    @staticmethod
    def model_to_dict(model):
        dict_resul = {}
        for k, v in model.__dict__.items():
            if type(v) in (str, unicode, bool, int, float):
                dict_resul[k] = v
        return dict_resul

    @staticmethod
    def deleteChidls(childs):
        lista = []
        for r in childs:
            if r.tipo_relation == "foreingKey":
                lista.append({'id': r.id})
                r.delete()
            elif r.tipo_relation == "MANYTOMANY":
                query = r.id_tabla_nexo + "=" +str(r.id)
                row_aux = Model(db_name=r.db_name, table_name=r.tabla_nexo)
                for nexo in row_aux.getAll(query=query):
                    lista.append({'id': nexo.id})
                    nexo.delete()

        return lista
