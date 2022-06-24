from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'A_Intro'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1

    ENDOWMENT = cu(10)
    ALLOCATOR_ROLE = "Allocator"
    RECIPIENT_ROLE = "Recipient"

    RECIPIENT_TEMPLATE = "A_Intro/C_Recipient.html"
    ALLOCATOR_TEMPLATE = "A_Intro/C_Allocator.html"


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


# PAGES
class A_Intro(Page):
    pass

class B_Instructions(Page):
    pass



page_sequence = [A_Intro, B_Instructions]
