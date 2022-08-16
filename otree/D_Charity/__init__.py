from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'D_Charity'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

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
    voiceBase64 = models.LongStringField(doc="base64 encoded voice input on decision screen.",
                                         blank=True)

    # baseline variable
    comprehensionAudio = models.LongStringField(doc="base64 encoded voice input on comprehension screen.",
                                                blank=True)

    # technical covariates (or web tracking)
    longitude = models.StringField(doc="the participant's location: longitude.", blank=True)
    latitude = models.StringField(doc="the participant's location: latitude.", blank=True)
    ipAddress = models.StringField(doc="the participant's IP address", blank=True)
    width = models.IntegerField(doc="the participant's screen width.", blank=True)
    height = models.IntegerField(doc="the participant's screen width.", blank=True)
    devicePixelRatio = models.IntegerField(doc="the participant's ratio of pixel sizes.", blank=True)
    userAgent = models.LongStringField(doc="get user agent, i.e. (unreliable) device info.", blank=True)

    # questionnaire
    comp_1 = models.IntegerField(
        label="On a scale ranging from 1 (not clear at all) to 5 (very clear), how well did you understand the instructions?",
        choices=[1, 2, 3, 4, 5],
        widget=widgets.RadioSelectHorizontal
    )

    # comp_1 = models.BooleanField(
    #     label="Did you understand the instructions?",
    #     blank=True,
    #     choices=[
    #         [False, 'No'],
    #         [True, 'Yes'],
    #     ]
    # )

    comp_2 = models.LongStringField(
        label="Was anything unclear?"
    )

    comp_3 = models.LongStringField(
        label="Would you prefer to donate to another charity? If so, which one?",
        blank=True
    )

    # demographics
    age = models.IntegerField(label="Please enter your age",
                              min=18,
                              max=99)

    gender = models.IntegerField(
        label="Please select your gender.",
        choices=[
            [1, "Female"],
            [2, "Male"],
            [3, "Diverse"],
        ]
    )

    education = models.IntegerField(
        label = "What is the highest level of education you achieved?",
        choices=[
            [1, "Some high school"],
            [2, "High school diploma or G.E.D."],
            [3, "Some college"],
            [4, "Associate's degree"],
            [5, "Bachelor's degree"],
            [6, "Master's degree"],
            [7, "Other"],
            [8, "Doctorate"],
        ]
    )

    income = models.IntegerField(
        label = "What is your total household income per year?",
        blank=True,
        choices=[
            [1, "Less than $10,000"],
            [2, "$10,000 to $19,999"],
            [3, "$20,000 to $34,999"],
            [4, "$35,000 to $49,999"],
            [5, "$50,000 to $74,999"],
            [6, "$75,000 to $99,999"],
            [7, "$100,000 to $149,999"],
            [8, "$150,000 or more"],
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
    form_fields = ["comprehensionAudio"]

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

    @staticmethod
    def js_vars(player):
        return dict(
            participant_label=player.participant.label,
            template="comprehension",
            allow_replay=True,
        )

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
            template="decision",
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

class G_Questionnaire(Page):
    form_model = "player"
    form_fields = ["comp_1", "comp_2", "comp_3"]
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )

class H_Demographics(Page):
    form_model = "player"
    form_fields = ["age", "gender", "education", "income"]
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )

class I_Outro(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

page_sequence = [A_Intro, B_Instructions, D_Comprehension, E_Decision, #F_Results,
                 G_Questionnaire, H_Demographics, I_Outro]
