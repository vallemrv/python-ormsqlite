# @Author: Manuel Rodriguez <valle>
# @Date:   20-Jul-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 06-Dec-2017
# @License: Apache license vesion 2.0


import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from valleorm.models import Field
#test for fields

field = Field()
print field.get_serialize_data('field')
