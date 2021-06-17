[![Build Status](https://travis-ci.org/Ermlab/python-ddd.svg?branch=master)](https://travis-ci.org/Ermlab/python-ddd)
[![codecov](https://codecov.io/gh/Ermlab/python-ddd/branch/master/graph/badge.svg)](https://codecov.io/gh/Ermlab/python-ddd)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# Inroduction

## The goal of this project

AUCTION APPLICATION

The goal is to implement an automatic bidding system using DDD tactical patterns, 
described here: https://www.ebay.co.uk/pages/help/buy/bidding-overview.html



# Domain

Online Auctions domain was selected for the purpose of this project, which is loosely based on Ebay bidding system.

The main reason for selecting this domain is general familiarity and limited complexity - many people understand how internet bidding work and the whole concept is not difficult to understand (or at least it's much simpler that healthcare or banking). On the other hand it's not simply a CRUD system - there are some business rules that must be implemented in the system.

## Domain description

### Item catalog

Item catalog is a place where `User`s can manage their `Item`s for sale. Item has a name, description and a starting price. Item can be in a `draft` state, or in a `ready` state.

When item is `ready` it can be `published` so that other users can bid for it. `Item` can be published manually or scheduled for publication at a given time.

### Bidding system

When `Item` is published, a bidding is started. Other users can place `Bid`s for the item by entering a maximum amount they are willing to pay for an item. An user with a a maximum bid is announced as a `winning bidder`, and all other bidding participants are notified.

After a fixed time since the bidding was started a bidding ends and the `Winner` is announced. 

### Payments

At this point, payments are out of scope for this project.

### Users

Each user can be a `Seller` or a `Buyer` (or both). User priveledges can be elevated to a `Staff member` or `Administrator`.


## Event storming

Event storming technique was used to discover the business domain and the most important business processes.

### User registration proceess

...

### Auction Item publication

...

### Bidding process

...