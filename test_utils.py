from utils import query_filter


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
