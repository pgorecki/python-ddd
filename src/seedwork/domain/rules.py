from pydantic import BaseModel


class BusinessRule(BaseModel):
    message: str = "This is an error message for broken business rule"

    def get_message(self) -> str:
        return self.message

    def is_broken(self) -> bool:
        pass
