# 4.   Separate commands and queries

Date: 2021-05-25

## Status

Accepted

## Context

We want to keep controllers as thin as possible. Therefore each controller should have access to a module, which exposes an interface allowing to read system state using `queries` and change system state using `commands`. However, keep in mind that this does not imply having separate read and write models (as in pure CQRS) - it's up to a module architecture if same or different models are needed.

```
def get_route_controller(request, module):
    module.execute_query(MyQuery(
        foo=request.GET.foo,
        bar=request.GET.bar,
    ))
    return Response(HTTP_200_OK)


def post_route_controller(request, module):
    result = module.execute(MyCommand(
        foo=request.POST.foo,
        bar=request.POST.bar,
    ))
    return Response(HTTP_200_OK)
```


## Consequences
- controllers are thin
- each module must implement `execute_query` and `execute_command` methods