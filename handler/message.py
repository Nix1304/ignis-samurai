import json

from utils.logger import Logger
from utils.vk.vk import VK
from utils.vk_utils import generate_random_id


class MessageArgs(dict):
    def __init__(self, args: dict):
        self.__args: dict = args
        super().__init__(args)

    def __getattr__(self, item):
        try:
            return self.__args[item]
        except KeyError:
            return None


class Message:
    __slots__ = ('session', 'api', 'raw', 'id', 'date', 'peer_id', 'from_id',
                 'chat_id', 'is_chat', 'original_text', 'text', 'attachments',
                 'payload', 'forwarded_messages', 'reply_message', 'meta')

    def __init__(self, session, api, raw: dict):
        self.session: VK = session
        self.api = api
        try:
            self.raw: dict = raw['message']
        except KeyError:
            self.raw: dict = raw

        self.id: int = self.raw.get('id', 0)
        self.date: int = self.raw['date']

        self.peer_id: int = self.raw['peer_id']
        self.from_id: int = self.raw['from_id']

        self.chat_id: int = self.peer_id - 2000000000
        self.is_chat: bool = self.chat_id > 0

        self.original_text: str = self.raw['text']
        self.text: str = self.original_text.lower()

        self.attachments: list = self.raw['attachments']

        self.payload: dict = json.loads(self.raw.get('payload', '{}'))

        self.forwarded_messages: list = self.raw.get('fwd_messages', [])
        self.reply_message = Message(self.session, self.api, self.raw['reply_message']) \
            if 'reply_message' in self.raw else None

        self.meta: dict = {}

    async def answer(self, text: str = '', attachments: (str, list, tuple, set, frozenset) = '', **kwargs):
        data = kwargs.copy()
        data.update({
            'peer_id': self.peer_id,
            'random_id': generate_random_id()
        })

        if text:
            data.update({'message': text})
        if attachments:
            if type(attachments) == str:
                data.update({'attachment': attachments})
            else:
                data.update({'attachment': ','.join(attachments)})
        await self.api.messages.send(**data)

    def __str__(self):
        return str(self.raw)

    def __repr__(self):
        return str(self.raw)
