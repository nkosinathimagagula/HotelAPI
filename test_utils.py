from utils import query_filter, createReferenceNumber


def test_query_filter():
    dummy_dictionary = {
        'one' : 1,
        'two': 2,
        'three': None,
        'four': 4,
        'five': None,
        'six': None
    }
    
    results = query_filter(dummy_dictionary)
    
    assert len(results) == 3
    assert list(results.keys()) == ['one', 'two', 'four']
    assert list(results.values()) == [1, 2, 4]


def test_create_reference_number():
    dummy_room_number = 'SC4499'
    
    results = createReferenceNumber(dummy_room_number)
    
    assert len(results) == 13
    assert type(results) == str
    assert results[1] == 'S'
    assert results[2] == '4'
    assert results[3] == '9'
