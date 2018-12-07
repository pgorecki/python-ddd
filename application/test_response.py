from datetime import datetime

from application.response import CustomJSONEncoder, json_response


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


def test_custom_json_encoder_for_date():
    current_date = datetime.now()
    data = {
        'date': current_date,
    }
    expected = (
        '{'
        f"\"date\": \"{current_date.isoformat() + 'Z'}\""
        '}'
    )

    actual = CustomJSONEncoder().encode(data)
    json_response_value = json_response(data)
    assert actual == expected
    assert json_response_value == expected


def test_custom_json_encoder_for_object_with_to_json_method():
    data = {
        'mock_object_to_json': MockObjectWithToJsonMethod('some text for to_json')
    }
    expected = '{"mock_object_to_json": {"desc": "some text for to_json"}}'

    actual = CustomJSONEncoder().encode(data)
    json_response_value = json_response(data)
    assert actual == expected
    assert json_response_value == expected


def test_custom_json_encoder_for_object_with_dict():
    data = {
        'mock_object_dict': MockObjectWithDictMethod('some text for __dict__'),
    }
    expected = '{"mock_object_dict": {"desc": "some text for __dict__"}}'

    actual = CustomJSONEncoder().encode(data)
    json_response_value = json_response(data)
    assert actual == expected
    assert json_response_value == expected


def test_custom_json_encoder_for_complex_object_with_dict():
    data = {
        'complex_json': MockComplexObjectWithDictMethod('title', 'some text for __dict__', 12.34),
    }
    expected = '{"complex_json": {"desc": "some text for __dict__", "title": "title", "value": 12.34}}'

    actual = CustomJSONEncoder().encode(data)
    json_response_value = json_response(data)
    assert actual == expected
    assert json_response_value == expected
