from django.conf.urls import url

from nmis.notices import consumers

websocket_urlpatterns = [
    url(r'^ws/staffs/(?P<staff_id>[^/]+)/$', consumers.ChatConsumer),
    # path(r'^ws/staffs/(?P<room_name>[^/]+)/$', consumers.ChatConsumer)
]