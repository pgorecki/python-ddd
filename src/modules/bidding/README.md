# Bidding bounded context

Bidding is competitively offering a price that the bidder or the person offering a bid is willing to pay for a commodity this commodity can be anything, cars, bikes, properties, etc. The price offered is called a bid, the person offering the price is called the bidder and the entire phenomenon is known as bidding.
https://www.educba.com/bidding-vs-auction/

## Bidding process

As a Buyer, you can place a bid, which must be greater than the current price + 1 USD and which sets the highest price you are willing to pay for an item. 
System will let you know (by email) if someone outbids you, and you can decide if you want to increase your maximum limit. 
Sometimes you can be automatically outbid (if some other buyer sets his maximum limit higher that yours).

For example:
1. Alice wants to sell X. She sets the ask price for this item as 10 USD. 
2. Bob wants to place a bid on X. The minimum amount is 10 USD (the ask price), and he places the bid of 15 USD. As the only bidder, he is the winner and the current price for X is 10 USD.
3. Alice and Bob are notified by email.
4. Charlie places his bid, but now the minimum price he can bid is 11 USD, so he decides to bid 12 USD. As this is not enough to outbid Bob, he is not the winner, and the price is increased to 12 USD.
5. Charlie places another bid, this time with the amount of 20 USD. As this is more than Bob's maximum limit, Charlie is the winner and the price is increased to 16 USD.
6. Alice is notified of new winner and price for X. Bob is notified by email that he is outbid.
7. Charlie decides to increase his maximum limit to 25 USD by bidding again with the increased amount.
8. Now if Bob wants to win the bidding, he must place a bid of at least 26 USD.


## Ubiquitous language

**Listing** - a product for sale

**Bidding** - a competitive process of offering a price for listing of a commodity for sale

**Seller** - the person selling a listing

**Bidder** - the person offering the price is called the bidder

**Bid** - a maximum price offered by a bidder to purchase a listing


## User stories:

- [x] As a bidder, I want to place a bid.

- [x] As a bidder, I want to retract a bid.
- 
- [ ] As a seller, I want to cancel my listing immediately.