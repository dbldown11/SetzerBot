async def get_card_list_by_rarity(rarity, pickable_cards, fallback_cards) -> list:
    cards = [card for card in pickable_cards if card['rarity'] == rarity]
    if len(cards) < 5:
        cards = [card for card in fallback_cards if card['rarity'] == rarity]
    return cards
