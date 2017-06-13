import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from valleorm.models import Models


reg = Models(tableName="user", dbName="valleorm.db")
tables = reg.__find_db_nexo__("user", "puesto")
