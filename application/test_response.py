from application.response import CustomJSONEncoder, json_response
from datetime import datetime
import json


class MockObjectWithToJsonMethod:
    def __init__(self, description: str):
        self.desc: str = description

    def to_json(self):
        return {
            'desc': self.desc
        }


class MockObjectWithDictMethod:
    def __init__(self, description: str):
        self.desc = description


class MockComplexObjectWithDictMethod:
    def __init__(self, title: str, description: str, value: float):
        self.title = title
        self.desc = description
        self.value = value


def test_custom_json_encoder():
    current_date = datetime.now()
    data = {
        'date': current_date,
        'mock_object_to_json': MockObjectWithToJsonMethod('some text for to_json'),
        'mock_object_dict': MockObjectWithDictMethod('some text for __dict__'),
        'complex_json': MockComplexObjectWithDictMethod('title', 'some text for __dict__', 12.34),
    }
    expected = (
        '{'
        f"\"date\": \"{current_date.isoformat()+'Z'}\""
        ', '
        f"\"mock_object_to_json\": \x7b\"desc\": \"some text for to_json\"\x7d"
        ', '
        f"\"mock_object_dict\": \x7b\"desc\": \"some text for __dict__\"\x7d"
        ', '
        f"\"complex_json\": \x7b\"desc\": \"some text for __dict__\", \"title\": \"title\", \"value\": 12.34\x7d"
        '}'
    )

    actual = CustomJSONEncoder().encode(data)
    json_response_value = json_response(data)
    assert actual == expected
    assert json_response_value == expected
