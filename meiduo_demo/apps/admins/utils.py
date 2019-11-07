def jwt_response_payload_handler(token, user=None, request=None):
    """
    自定义jwt认证成功返回数据
    """
    return {
        'username': user.username,
        'id': user.id,
        'token': token,
    }