# coding=utf-8
#
# Created on 2018-5-29, by Junn
#

from rest_framework import serializers

from base.serializers import BaseModelSerializer
from nmis.hospitals.models import  Hospital, Staff


class HospitalSerializer(BaseModelSerializer):
    # avatar = serializers.SerializerMethodField('get_avatar')

    class Meta:
        model = Hospital
        fields = (
            'id', 'organ_name',
        )


class StaffSerializer(BaseModelSerializer):
    class  Meta:
        model = Staff
        fields = (
            'id', 'organ_id', 'dept_id', 'group_id', 'user_id', 'name', 'title',
            'contact', 'email', 'status', 'created_time',
        )