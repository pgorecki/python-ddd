# 4.   Error handling during operation execution

Date: 2021-05-25

## Status

Pending

## Context

When executing an operation (command or query), many bad things can happen. This can be related to access permission, data validation, business rule validation, infrastructure errors, etc. We need to collect and handle such errors in an unified way for further processing (API responses, UI notifications for a user). The solution should also support a way to convert errors into meaningful messages for an end user (including language translations).

## Possible solutions
1. Raise an exception during operation processing. This solutioun relies on throwing an exception during command execution and handling it somewhere upper in the call stack. 

Pros:
- can throw exception from anywhere

Cons:
- non-linear program flow can become a mess really quickly because it’s hard to trace all existing connections between throw and catch statements.

2. Explicitly return values indicating success or failure of an operation instead of throwing exceptions using a `Result` class. Expected erros should be reported to a `Result` object. Unexpected errors should be handled using exceptions.

Pros:
- can return multiple errors within one operation

Cons:
- ...

## Decision

TBA


## Consequences

....