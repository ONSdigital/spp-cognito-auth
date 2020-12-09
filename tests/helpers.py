from uuid import UUID


def is_valid_uuid(uuid_to_test):
    try:
        print(uuid_to_test)
        uuid = UUID(uuid_to_test, version=4)
    except ValueError:
        return False
    return str(uuid) == uuid_to_test
