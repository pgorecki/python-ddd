from dependency_injector.wiring import Provide
from fastapi import Depends


def dependency(provider):
    """Turns DI provider into FastAPI dependency"""
    return Depends(Provide[provider])
