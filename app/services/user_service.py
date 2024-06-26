import asyncio

from app.database import repository
from app.database.database_connection import Collections
from app.log.log import log_decorator
from app.models.user import User
from app.services import revenue_service, expense_service


@log_decorator('app.log')
async def get_users():
    """
    Retrieve all users from the database.
    Returns:
        list: A list of user documents from the database.
    Raises:
        Exception: If there is an error during the retrieval process.
    """
    try:
        return await repository.get_all(Collections.users)
    except Exception as e:
        raise e


@log_decorator('app.log')
async def get_user_by_id(user_id: str):
    """
    Retrieve a user by their ID.
    Args:
        user_id (str): The ID of the user to retrieve.
    Returns:
        dict: The user document if found.
    Raises:
        ValueError: If the user is not found.
        Exception: If there is an error during the retrieval process.
    """
    try:
        return await repository.get_by_id(Collections.users, user_id)
    except Exception as e:
        raise e


@log_decorator('app.log')
async def add_user(new_user: User):
    """
    Add a new user to the database.
    Args:
        new_user (User): The user object to add.
    Returns:
        dict: The added user document.
    Raises:
        ValueError: If the user object is null or the user ID already exists.
        Exception: If there is an error during the addition process.
    """
    if new_user is None:
        raise ValueError("User object is null")
    if await get_user_by_id(new_user.id) is not None:
        raise ValueError("User ID already exists")
    try:
        return await repository.add(Collections.users, new_user.dict())
    except Exception as e:
        raise e


@log_decorator('app.log')
async def login(email, password):
    """
    Authenticate a user based on their email and password.
    Args:
        email (str): The email address of the user.
        password (str): The password of the user.
    Returns:
        dict: The authenticated user document.
    Raises:
        ValueError: If email or password is not provided, or if the user is not found, or if the password is incorrect.
        Exception: If there is an error during the authentication process.
    """
    if email is None or password is None:
        raise ValueError("Please enter all values")
    try:
        users = await get_users()
        user = next((u for u in users if u['email'] == email), None)
        if user is None:
            raise ValueError("User not found")
        if not password == user['password']:
            raise ValueError("Invalid password")
        return user
    except Exception as e:
        raise ValueError(e)


@log_decorator('app.log')
async def update_user(user_id: str, updated_data: User):
    """
    Update an existing user's data.
    Args:
        user_id (str): The ID of the user to update.
        updated_data (User): The updated user object.
    Returns:
        dict: The updated user document.
    Raises:
        ValueError: If the user object is null or the user is not found.
        Exception: If there is an error during the update process.
    """
    try:
        return await repository.update(Collections.users, user_id, updated_data.dict())
    except Exception as e:
        raise e


@log_decorator('app.log')
async def delete_user(user_id: str):
    """
    Delete a user from the database.
    Args:
        user_id (str): The ID of the user to delete.
    Returns:
        dict: The deleted user document.
    Raises:
        ValueError: If the user is not found.
        Exception: If there is an error during the deletion process.
    """
    existing_user = await get_user_by_id(user_id)
    if existing_user is None:
        raise ValueError("User not found")
    try:
        # Get user's revenues and expenses concurrently
        revenues_task = revenue_service.get_revenues(user_id)
        expenses_task = expense_service.get_expenses(user_id)

        # Await both tasks concurrently
        revenues, expenses = await asyncio.gather(revenues_task, expenses_task)

        # Delete user's revenues and expenses concurrently
        delete_revenues_task = [revenue_service.delete_revenue(revenue['id'], user_id) for revenue in revenues]
        delete_expenses_task = [expense_service.delete_expense(expense['id'], user_id) for expense in expenses]

        # Await deletion of revenues and expenses concurrently
        await asyncio.gather(*delete_revenues_task, *delete_expenses_task)

        # Finally, delete the user
        deleted_user = await repository.delete(Collections.users, user_id)
        deleted_user['balance'] = existing_user['balance']
        return deleted_user
    except (ValueError, RuntimeError, Exception) as e:
        raise e
