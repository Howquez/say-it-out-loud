from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'D_Charity'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 5

    ENDOWMENT = cu(10)
    RULES_TEMPLATE = "D_Charity/C_Rules.html"


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # treatment variable
    voice_interface = models.BooleanField(doc="treatment variable describing whether the allocator communicates his/her decision orally.")

    # primary outcome variable
    share = models.IntegerField(doc="the share the dictator allocates to the recipient.",
                                min=0,
                                blank=True,
                                initial=0)  # reconsider this part.
    voiceBase64 = models.LongStringField(doc="base64 encoded voice input.")

    # technical covariates (or web tracking)
    longitude = models.StringField(doc="the participant's location: longitude.", blank=True)
    latitude = models.StringField(doc="the participant's location: latitude.", blank=True)
    ipAddress = models.StringField(doc="the participant's IP address", blank=True)
    width = models.IntegerField(doc="the participant's screen width.", blank=True)
    height = models.IntegerField(doc="the participant's screen width.", blank=True)
    devicePixelRatio = models.IntegerField(doc="the participant's ratio of pixel sizes.", blank=True)
    userAgent = models.LongStringField(doc="get user agent, i.e. (unreliable) device info.", blank=True)

    # comprehension
    comp_1 = models.BooleanField(
        label="Everything clear?",
        blank=False,
        choices=[
            [False, 'No'],
            [True, 'Yes'],
        ]
    )


# FUNCTIONS
def creating_session(subsession):
    import itertools
    voice_interface = itertools.cycle([True, False])
    for player in subsession.get_players():
        player.voice_interface = next(voice_interface)


# PAGES
class A_Intro(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

class B_Instructions(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )

class D_Comprehension(Page):
    form_model = "player"
    form_fields = ["comp_1"]

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )

class E_Decision(Page):
    form_model = "player"
    form_fields = ["share", "voiceBase64",
                   "longitude", "latitude", "ipAddress", "width", "height", "devicePixelRatio", "userAgent"]

    @staticmethod
    def js_vars(player):
        return dict(
            participant_label=player.participant.label,
            allow_replay=False,
        )

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect = "",
        )


# class ResultsWaitPage(WaitPage):
#     pass


class F_Results(Page):
    @staticmethod
    def js_vars(player):
        dic_share = (1 - (player.share / 10)) * 100
        return dict(
            dictators=dic_share,
            role="Allocator"
        )

class G_Outro(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

page_sequence = [A_Intro, B_Instructions, D_Comprehension, E_Decision, F_Results, G_Outro]
