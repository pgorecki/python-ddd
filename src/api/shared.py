from fastapi import Depends
from dependency_injector.wiring import Provide


def dependency(provider):
    """Turns DI provider into FastAPI dependency"""
    return Depends(Provide[provider])
