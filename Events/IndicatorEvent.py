import json
from datetime import datetime

from Events.IEvent import IEvent


class IndicatorEvent(IEvent):
    def __init__(self, instrument, time, value):
        self.instrument = instrument
        self.time = time
        self.value = value

    def to_json(self):
        def stuff_to_string(data):
            if isinstance(data, datetime):
                return data.strftime("%Y-%m-%dT%H:%M:%S")
            else:
                return data.__dict__
        return json.dumps(self, default=stuff_to_string, sort_keys=True, )

    @staticmethod
    def from_json(data):
        return IndicatorEvent(data['instrument'], datetime.strptime(data['time'], "%Y-%m-%dT%H:%M:%S"), data['value'])
