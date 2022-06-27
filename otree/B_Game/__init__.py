from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'B_Game'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 5

    ENDOWMENT = cu(10)
    ALLOCATOR_ROLE = "Allocator"
    RECIPIENT_ROLE = "Recipient"

    RECIPIENT_TEMPLATE = "A_Intro/C_Recipient.html"
    ALLOCATOR_TEMPLATE = "A_Intro/C_Allocator.html"


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    voice_interface = models.BooleanField(doc="treatment variable describing whether the allocator communicates his/her decision orally.")



class Player(BasePlayer):
    share = models.IntegerField(doc="the share the dictator allocates to the recipient.",
                                min=0,
                                blank=True,
                                initial=0) # reconsider this part.

# FUNCTIONS
def creating_session(subsession):
    import itertools
    voice_interface = itertools.cycle([True, False])
    for group in subsession.get_groups():
        group.voice_interface = next(voice_interface)


# PAGES
class A_Decision(Page):
    form_model = "player"
    form_fields = ["share"]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect = "",
        )



class ResultsWaitPage(WaitPage):
    pass


class Results(Page):
    @staticmethod
    def js_vars(player):
        dic_share = (1 - player.group.get_player_by_role(C.ALLOCATOR_ROLE).share / 10) * 100
        return dict(
            dictators=dic_share,
            role=player.role
        )
    pass


page_sequence = [A_Decision, ResultsWaitPage, Results]
