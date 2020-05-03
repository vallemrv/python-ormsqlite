# @Author: Manuel Rodriguez <vallemrv>
# @Date:   29-Aug-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 06-Sep-2017
# @License: Apache license vesion 2.0
import sys
from .constant import *
from .fields import *
from .relatedfields import *
from .model import Model
from .tools import Utility, Q
from .qsonhelper import QSonHelper



def migrate_models(alter=False, models=[]):
    for m in models:
        if alter or not Utility.exists_table(Utility.default_tb_name(m), Utility.default_db_name(m)):
            m.init_model()
            
