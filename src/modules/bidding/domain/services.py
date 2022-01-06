# TODO: Work in progress...


class EndListingPolicy:
    def end_listing(self, listing):
        specification = EndListingSpecification()
        if specification.is_satisfied_by(listing):
            command = EndListingCommand(...)
            dispatch(command)


class EndingListingService(ApplicationService):
    def end_pastdue_listings(self):
        listing_ids = get_listing_ids_for_overdue_listings()

        # v1
        for listing_id in listing_ids:
            listing = listing_repository.get_by_id(listing_id)
            events = listing.end()
            events_publisher.publish(events)

        # v2
        policy = EndListingPolicy()
        for listing_id in listing_ids:
            listing = listing_repository.get_by_id(listing_id)
            policy.end_listing(listing)
