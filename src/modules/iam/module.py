from seedwork.application.modules import BusinessModule

from modules.iam.application.services import AuthenticationService


class IdentityAndAccessModule(BusinessModule):
    def __init__(self, authentication_service: AuthenticationService):
        self.authentication_service = authentication_service

    # @staticmethod
    # def create(container):
    #     assert False
    #     """Factory method for creating a module by using dependencies from a DI container"""
    #     return IdentityAndAccessModule(
    #         logger=container.logger(),
    #         authentication_service=container.authentication_service(),
    #     )
