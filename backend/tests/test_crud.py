"""Tests for CRUD operations."""

from app.crud import list_messages, create_message
from app.models import Message


async def test_create_message_async(async_test_db_session, mock_db_time):
    """Test creating a message asynchronously."""
    with mock_db_time(model=Message) as mocked_time:
        new_message = Message(content="Test message for CRUD")
        db_message = await create_message(async_test_db_session, new_message)

    assert db_message.id == 1
    assert db_message.content == "Test message for CRUD"
    assert db_message.created_at == mocked_time

async def test_list_messages_empty_async(async_test_db_session):
    """Test listing messages when database is empty."""
    # Now call the actual crud.list_messages function
    messages = await list_messages(async_test_db_session)
    assert isinstance(messages, list)
    assert len(messages) == 0


def test_list_messages_with_pagination_sync(test_db_session):
    """Test listing messages with pagination."""
    # Create some messages
    for i in range(5):
        message = Message(content=f"Message {i}")
        test_db_session.add(message)
    test_db_session.commit()
    
    # Test skip and limit
    messages = test_db_session.query(Message).offset(2).limit(2).all()
    assert len(messages) == 2
    assert isinstance(messages, list)


def test_create_message_without_flush(test_db_session):
    """Test creating a message and committing directly."""
    message = Message(content="Direct commit test")
    test_db_session.add(message)
    test_db_session.commit()
    
    # Query the message back
    saved_message = test_db_session.query(Message).filter_by(content="Direct commit test").first()
    assert saved_message is not None
    assert saved_message.content == "Direct commit test"


def test_list_messages_with_large_offset(test_db_session):
    """Test listing messages with offset larger than available records."""
    # Create 3 messages
    for i in range(3):
        message = Message(content=f"Message {i}")
        test_db_session.add(message)
    test_db_session.commit()
    
    # Query with large offset
    messages = test_db_session.query(Message).offset(10).limit(5).all()
    assert len(messages) == 0



async def test_list_messages_with_fixture(async_db_with_messages):
    """
    Test calling crud.list_messages async function with fixture-populated data.
    Uses the async_db_with_messages fixture for a clean async session with data.
    """
    # Now call the actual crud.list_messages function
    messages = await list_messages(async_db_with_messages, skip=0, limit=100)
    
    # Assert we get the correct list of Message objects
    assert isinstance(messages, list)
    assert len(messages) == 3
    assert all(isinstance(msg, Message) for msg in messages)
    assert messages[0].content == "First test message"
    assert messages[1].content == "Second test message"
    assert messages[2].content == "Third test message"
    
    # Test with pagination
    paginated = await list_messages(async_db_with_messages, skip=1, limit=2)
    assert len(paginated) == 2
    assert paginated[0].content == "Second test message"
    assert paginated[1].content == "Third test message"


async def test_list_messages_with_fixture_pagination(async_db_with_messages):
    """
    Test pagination with fixture-populated data (3 messages).
    """
    from app.models import Message
    
    # Test skip=1, limit=2 - should get messages 2 and 3
    messages = await list_messages(async_db_with_messages, skip=1, limit=2)
    
    assert len(messages) == 2
    assert messages[0].content == "Second test message"
    assert messages[1].content == "Third test message"
    
    # Test skip=0, limit=2 - should get messages 1 and 2
    messages = await list_messages(async_db_with_messages, skip=0, limit=2)
    
    assert len(messages) == 2
    assert messages[0].content == "First test message"
    assert messages[1].content == "Second test message"
