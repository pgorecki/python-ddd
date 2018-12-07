from application.queries import GetItemsQuery

def test_valid_get_items_query():
    query = GetItemsQuery()
    assert query.is_valid() == True