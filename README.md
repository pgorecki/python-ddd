AUCTION APPLICATION

The goal is to implement an automatic bidding system, described here: https://www.ebay.co.uk/pages/help/buy/bidding-overview.html


TODO for near future:

* commands, command bus and handlers

* executing commands with immediate feedback
  http://blog.sapiensworks.com/post/2015/07/20/CQRS-Immediate-Feedback-Web-App

* handling commands errors: application layer, business layer

* start using dependency injection

* command validation
  https://stackoverflow.com/questions/32239353/command-validation-in-ddd-with-cqrs

* handling async commands


User stories:

* As a seller I can list a new item for sale. The item has the following fields: text, description, starting price

* As a seller, I'm allowed to list up to 3 items at the same time

* As a user I can view all the items for sale. For each item I will see: text, description, current price, minimum bidding price, a winner, all participants, action end date

* As a bidder, when placing a bid, I enter the maximum amount I am willing to pay for the item. The seller and other bidders don't know my maximum bid

* As a bidder, when placing a bid, my bid must be higher than the actual price

* Auction Store will automatically calculate the current price of an item based on the bids that were made

* When auction ends, auction store will notify the seller by email. The email will contain the name of the winner and the sell price.

* When auction ends, all losing participants will recieve an email with the information that they lost an auction. 

* When auction ends, the winning participant will reciewve an email with information the user has won and the price for an item.




```
pipenv install
pipenv shell
```

To run tests
```
pytest
```

To run tests in watch mode
```
ptw
```

To run the app as Falcon server
```
FRAMEWORK=falcon gunicorn --reload main
```

To run the app as Flask server
```
FRAMEWORK=flask gunicorn --reload main
```


Project structure:

```
context-1
  domain
    entities
    value_objects
    aggregates
    services
    repositories
    factories?
    interfaces
    events
  application
    services
  infrastructure
    ??
  tests??

context-2

context-3

di_setup
main - main entrypoint to the app
```

Domain artifacts

* entities - mutable, identifiable, unaware of persistance

* value objects - immutable, self-contained

* aggregates - any transaction should modify only one aggegate at a time, 70-80% usually contain olny one entity, consistency boundary, hosts methods which will modify the aggregate

* events - significant state transition, something which domain experts care about

* factories - for entity construction, ubiquotous language verbs, hide construction details (Python function)

* repositories - store aggregates, abstraction over persistence mehanism

* context maps - mappings between concepts between bounded contexts

TODO:
 * event bus? for domain
 
References:

* Command design pattern: https://www.youtube.com/watch?v=9qA5kw8dcSU

* https://skillsmatter.com/skillscasts/5025-domain-driven-design-with-python(python-ddd)