from fastapi import HTTPException

class AppError(HTTPException):
    def __init__(
        self,
        status_code: int,
        error_code: str,
        user_message: str,
        message: str | None = None,
    ):
        super().__init__(status_code=status_code, detail=message)
        self.error_code = error_code
        self.user_message = user_message

class AICreditsExceededError(AppError):
    def __init__(self):
        super().__init__(
            status_code=402,
            error_code="AI_CREDITS_EXCEEDED",
            user_message="Seu limite de uso da IA foi atingido. Tente novamente mais tarde ou entre em contato com o suporte.",
        )


class AIServiceUnavailableError(AppError):
    def __init__(self):
        super().__init__(
            status_code=503,
            error_code="AI_SERVICE_UNAVAILABLE",
            user_message="O serviço de inteligência artificial está temporariamente indisponível.",
        )


class ContractGenerationError(AppError):
    def __init__(self):
        super().__init__(
            status_code=500,
            error_code="CONTRACT_GENERATION_FAILED",
            user_message="Não foi possível gerar o contrato. Verifique os dados e tente novamente.",
        )


class InvalidUserInputError(AppError):
    def __init__(self, user_message: str):
        super().__init__(
            status_code=400,
            error_code="INVALID_INPUT",
            user_message=user_message,
        )
