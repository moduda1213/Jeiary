from fastapi import HTTPException, status

class ExpiredTokenException(HTTPException):
    """
    JWT 토큰이 만료되었을 때 발생하는 예외
    """
    def __init__(self, detail:str = "토큰이 만료되었습니다.."):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )
class InvalidTokenException(HTTPException):
    """
    JWT 토큰이 유효하지 않을 때 발생하는 예외
    """
    def __init__(self, detail:str = "유효하지 않은 토큰입니다."):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        ) 
        
class CredentialException(HTTPException):
    """
    자격 증명(로그인 등) 실패 시 발생하는 예외
    """
    def __init__(self, detail:str = "자격 증명에 실패하였습니다."):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )
        
class AIConnectionError(Exception):
    pass
        
class AIParsingError(Exception):
    pass