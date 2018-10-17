# coding=utf-8
#
# Created by gonghuaiqian, on 2018-10-16
#

import logging

from base.forms import BaseForm
from nmis.devices.models import FaultType, RepairOrder
from nmis.hospitals.models import Staff

logger = logging.getLogger(__name__)


class RepairOrderCreateForm(BaseForm):

    def __init__(self, user_profile, data, *args, **kwargs):
        BaseForm.__init__(self, data, *args, **kwargs)
        self.user_profile = user_profile
        self.data = data

    ERR_CODES = {

    }

    def is_valid(self):
        return True

    def save(self):
        applicant_id = self.data.get('applicant_id')
        fault_type_id = self.data.get('fault_type_id')
        desc = self.data.get('desc').strip()
        applicant = Staff.objects.get_by_id(applicant_id)
        fault_type = FaultType.objects.get_by_id(fault_type_id)
        return RepairOrder.objects.create_order(applicant, fault_type, desc, self.user_profile)
