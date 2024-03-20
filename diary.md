## Seedwork


## Architecture of Catalog module (2021-05-25)

What kind of architecture should we choose for the *Catalog* module? Should we use CQRS or maybe something simpler and easier to implement? Let's see what others says about it?

> CQRS stands for Command Query Responsibility Segregation. It's a pattern that I first heard described by Greg Young. At its heart is the notion that you can use a different model to update information than the model you use to read information. For some situations, this separation can be valuable, but beware that for most systems CQRS adds risky complexity. [1]

Since *Catalog* module is mostly about managing list items, it will likely contain a lot of CRUD-like functionality. We don't need separate read and writes models in this case, it seems like an overkill to me. So having full CQRS is not worth it. However, sticking to separation of commands and queries still looks tempting. Let's check out the alternatives:

1. "The typical entry point for this in DDD is an Application Service. Application services orchestrate calls to repositories and domain objects" [2][3].


Maybe we could implementing using a generic CRUD handler?


## Handling commands

The typical way of reading the system state via queries and changing the system state is via comands. The high-level route controller code could look like:

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

In this case `execute_command` is responsible for passing a command to an appriopriate command handler.


Keep in mind this is a happy path and bad things can happen along a way. In particular:
- creating command can fail: i.e.  command can have incorrect params, or some params can be missing (command param validation) [400]
- command execution can fail due to numerous reasons:
    - an object that we want act upon may not exist [404]
    - a user may not have permissions to perform certain command [403]
    - business rule may fail [400]
    - application level policy may fail, i.e. too many requests issued by the same user [429]
    - ....



For example, query or command can be invalid, an , user may


References:

- [1] https://martinfowler.com/bliki/CQRS.html
- [2] https://softwareengineering.stackexchange.com/questions/302187/crud-operations-in-ddd
- [3] https://lostechies.com/jimmybogard/2008/08/21/services-in-domain-driven-design/






## Other references

- https://github.com/VaughnVernon/IDDD_Samples/tree/master