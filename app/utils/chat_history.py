def delete_chat_history(user_id, user_conversations):
    """
    ragchain memory 삭제
    """
    # user_conversations[user_id].memory.clear()
    del user_conversations[user_id]
