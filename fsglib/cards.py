#!/usr/bin/env python3
import dataclasses, enum, random, io

class Card:
    """
    Base class for cards
    """
    pass

@dataclasses.dataclass(frozen=True, slots=True)
class PointCard(Card):
    """
    Cards that has points as values.
    """
    value : int

pointcards = (PointCard(1), PointCard(2), PointCard(5), PointCard(10))

class Actions(enum.Enum):
    """
    Enums representing actions for cards
    """
    SWAP = 1
    STEAL = 2
    DISCARD = 3
    EXTEND = 4
    PEEK = 5
    REFILL = 6
    DEDUCT = 7

@dataclasses.dataclass(frozen=True, slots=True)
class ActionCard(Card):
    """
    Cards that allow you to do more
    """
    action : Actions


actioncards = (
    ActionCard(Actions.SWAP),
    ActionCard(Actions.STEAL),
    ActionCard(Actions.DISCARD),
    ActionCard(Actions.EXTEND),
    ActionCard(Actions.PEEK),
    ActionCard(Actions.REFILL),
    ActionCard(Actions.DEDUCT)
    )

cards = [*pointcards, *actioncards]
random.shuffle(cards)
cards = tuple(cards)

def strcard(card : Card) -> str:
    if isinstance(card, ActionCard):
        card : ActionCard = card
        if card.action == Actions.SWAP:
            return str("Action card to swap with your opponent's deck")
        elif card.action == Actions.STEAL:
            return str("Action card to steal a card from your opponent's deck at random")
        elif card.action == Actions.DISCARD:
            return str("Action card to force your opponent to discard a card from their deck at random")
        elif card.action == Actions.EXTEND:
            return str("Action card to add 7 more rounds to this game")
        elif card.action == Actions.PEEK:
            return str("Action card to peek at your opponent's deck")
        elif card.action == Actions.REFILL:
            return str("Discard everyone's deck and give them new decks")
        elif card.action == Actions.DEDUCT:
            return str("Deduct your opponent's points by 5")
        else:
            return str("Unknown action card")
    elif isinstance(card, PointCard):
        card : PointCard = card
        return str(f"Point card of {card.value} points")
    else:
        return str(card)
    
def strdeck(deck : list[Card]) -> str:
    listed = io.StringIO()
    for index, card in enumerate(deck):
        print(f"{index} - {strcard(card)}", file=listed)
    return listed.getvalue()