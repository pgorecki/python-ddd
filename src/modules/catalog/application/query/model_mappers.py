from modules.catalog.infrastructure.listing_repository import ListingModel


def map_listing_model_to_dao(instance: ListingModel):
    """maps ListingModel to a data access object (a dictionary)"""
    data = instance.data
    return dict(
        id=instance.id,
        title=data["title"],
        description=data["description"],
        ask_price_amount=data["ask_price"]["amount"],
        ask_price_currency=data["ask_price"]["currency"],
        seller_id=data["seller_id"],
    )
