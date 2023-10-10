from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExecutionStep:
    task: Any
    handler: Any
    result: Any


@dataclass
class ExecutionChain:
    """This class captures the sequence of execution steps and their results during command/event execution."""

    steps: list[ExecutionStep] = field(default_factory=list)

    def add(self, step: ExecutionStep):
        self.steps.append(step)

    def is_success(self):
        return all([r.is_success() for r in self.steps])

    def triggered_events(self, type_of=None):
        all_events = []
        for step in self.steps:
            all_events.extend(step.result.events if step.result else [])

        if type_of:
            return list(filter(lambda e: isinstance(e, type_of), all_events))
        return all_events

    def extend(self, chain):
        self.steps.extend(chain.steps)

    @property
    def payload(self):
        command_result = self.steps[0].result
        return command_result.payload if command_result else None

    @classmethod
    def one(cls, step: ExecutionStep):
        chain = cls()
        chain.add(step)
        return chain
