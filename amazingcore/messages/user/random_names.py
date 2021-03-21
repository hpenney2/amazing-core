from amazingcore.messages.message_interfaces import Message, SerializableMessage
from amazingcore.codec.bit_stream import BitStream

import random
FAMILY_1 = ['Carrot', 'Chipper', 'Cucumber', 'Dimen', 'Floppy', 'Gall', 'Harv', 'Hearth', 'Hed',
            'Ice', 'Kect', 'Knobb', 'Moto', 'New', 'Shill', 'Soap', 'Sprinkle', 'Stauch', 'Swash', 'Whirl']
FAMILY_2 = ['any', 'edil', 'ellar', 'err', 'ian', 'ilil', 'ilir', 'ilsa', 'ilwen', 'isri',
            'it', 'mind', 'ow', 'palu', 'ping', 'quana', 'sasts', 'sila', 'taun', 'thstl', 'vala']
FAMILY_3 = ['able', 'actor', 'blink', 'booster', 'cobbler', 'cycle', 'enel', 'falls', 'ford', 'fun', 'gill', 'iston', 'izla',
            'ja', 'lia', 'ling', 'master', 'ne', 'nella', 'puddle', 'saurus', 'snap', 'soap', 'stormer', 'tickle', 'trove', 'well']


class RandomNamesMessage(Message):
    def __init__(self):
        self.request: RandomNamesRequest = RandomNamesRequest()
        self.response: RandomNamesResponse = RandomNamesResponse()

    async def process(self):
        if self.request.name_part_type == 'Family_1':
            self.response.names = random.sample(FAMILY_1, self.request.amount)
        elif self.request.name_part_type == 'Family_2':
            self.response.names = random.sample(FAMILY_2, self.request.amount)
        elif self.request.name_part_type == 'Family_3':
            self.response.names = random.sample(FAMILY_3, self.request.amount)
        else:
            raise NotImplementedError('unknown random name type')


class RandomNamesRequest(SerializableMessage):
    def __init__(self):
        self.amount: int = None
        self.name_part_type: str = None

    def serialize(self, bit_stream: BitStream):
        raise NotImplementedError

    def deserialize(self, bit_stream: BitStream):
        bit_stream.read_start()
        self.amount = bit_stream.read_int()
        self.name_part_type = bit_stream.read_str()

    def __str__(self):
        return str({'amount': self.amount, 'name_part_type': self.name_part_type})


class RandomNamesResponse(SerializableMessage):
    def __init__(self):
        self.names: list(str) = []

    def serialize(self, bit_stream: BitStream):
        bit_stream.write_start()
        bit_stream.write_int(len(self.names))
        for name in self.names:
            bit_stream.write_str(name)

    def deserialize(self, bit_stream: BitStream):
        raise NotImplementedError

    def __str__(self):
        return str({'names': self.names})