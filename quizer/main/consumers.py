import json
from asgiref.sync import async_to_sync

from channels.generic.websocket import WebsocketConsumer


class RunningTestsConsumer(WebsocketConsumer):

    group_name: str = 'running_tests'

    def connect(self):
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        received_dict = json.loads(text_data)
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'action',
                'action': received_dict['action']
            }
        )

    def action(self, event):
        action = event['action']
        self.send(text_data=json.dumps({
            'action': action
        }))
