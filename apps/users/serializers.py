#coding=utf-8
#
# Created on 2016-12-04, by Junn
#

from base.serializers import BaseModelSerializer
from users.models import User


class UserSerializer(BaseModelSerializer):
    # avatar = serializers.SerializerMethodField('get_avatar')

    class Meta:
        model = User
        fields = (
            'id', 'username','email', 'phone', 'gender', 'acct_type', 'login_count',
        )
        

