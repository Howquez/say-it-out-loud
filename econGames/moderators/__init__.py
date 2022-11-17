from otree.api import *
import random

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'mod'
    PLAYERS_PER_GROUP = None
    TASKS = ["A", "B", "C", "D"]
    NUM_ROUNDS = len(TASKS)

    MODERATORS_TEMPLATE = "moderators/T_Moderators.html"


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
# Greed avoidance
    greed_avoidance_1 = models.IntegerField(
        doc="I have a strong need for power.",
        label="I have a strong need for power.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7]
    )

    greed_avoidance_2 = models.IntegerField(
        doc="I seek status.",
        label="I seek status.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7]
    )

    greed_avoidance_3 = models.IntegerField(
        doc="I am mainly interested in money.",
        label="I am mainly interested in money.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7]
    )

    greed_avoidance_4 = models.IntegerField(
        doc="I am out for my own personal gain.",
        label="I am out for my own personal gain.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7]
    )


# Equity / Fairness
    equity_1 = models.IntegerField(
        doc="I treat all people equally.",
        label="I treat all people equally.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7]
    )

    equity_2 = models.IntegerField(
        doc="I believe that everyone's rights are equally important.",
        label="I believe that everyone's rights are equally important.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7]
    )

    equity_3 = models.IntegerField(
        doc="I give everyone a chance.",
        label="I give everyone a chance.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7]
    )

    equity_4 = models.IntegerField(
        doc="I am committed to principles of justice and equality.",
        label="I am committed to principles of justice and equality.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7]
    )

    equity_5 = models.IntegerField(
        doc="I help people even when I do not want to, because it is the right thing to do.",
        label="I help people even when I do not want to, because it is the right thing to do.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7]
    )

    equity_6 = models.IntegerField(
        doc="I take advantage of others. ",
        label="I take advantage of others. ",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7]
    )


# Expressiveness
    expressiveness_1 = models.IntegerField(
        doc="I talk a lot.",
        label="I talk a lot.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7]
    )

    expressiveness_2 = models.IntegerField(
        doc="I have an intense, boisterous laugh.",
        label="I have an intense, boisterous laugh.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7]
    )

    expressiveness_3 = models.IntegerField(
        doc="I don't like to draw attention to myself.",
        label="I don't like to draw attention to myself.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7]
    )

    expressiveness_4 = models.IntegerField(
        doc="I speak softly.",
        label="I speak softly.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7]
    )

    expressiveness_5 = models.IntegerField(
        doc="I am never at a loss for words.",
        label="I am never at a loss for words.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7]
    )


# Public Self Consciousness
    public_self_1 = models.IntegerField(
        doc="I care a lot about how I present myself to others.",
        label="I care a lot about how I present myself to others.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7]
    )

    public_self_2 = models.IntegerField(
        doc="I usually worry about making a good impression.",
        label="I usually worry about making a good impression.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7]
    )

    public_self_3 = models.IntegerField(
        doc="Before I leave my house, I check how I look.",
        label="Before I leave my house, I check how I look.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7]
    )

    public_self_4 = models.IntegerField(
        doc="I am usually aware of my appearance.",
        label="I am usually aware of my appearance.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7]
    )

    public_self_5 = models.IntegerField(
        doc="I am concerned about what people think of me.",
        label="I am concerned about what people think of me.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7]
    )



# FUNCTIONS
def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        for p in subsession.get_players():
            round_numbers = list(range(1, C.NUM_ROUNDS + 1))
            random.shuffle(round_numbers)
            page_sequence = dict(zip(C.TASKS, round_numbers))
            p.participant.page_sequence = page_sequence



# PAGES
class Greed_Avoicance(Page):
    form_model = "player"

    @staticmethod
    def get_form_fields(player: Player):
        form_fields = ["greed_avoidance_1", "greed_avoidance_2", "greed_avoidance_3", "greed_avoidance_4"]
        random.shuffle(form_fields)
        return form_fields

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.participant.page_sequence['A']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )

class Equity(Page):
    form_model = "player"

    @staticmethod
    def get_form_fields(player: Player):
        form_fields = ["equity_1", "equity_2", "equity_3", "equity_4", "equity_5", "equity_6"]
        random.shuffle(form_fields)
        return form_fields

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.participant.page_sequence['B']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )

class Expressiveness(Page):
    form_model = "player"

    @staticmethod
    def get_form_fields(player: Player):
        form_fields = ["expressiveness_1", "expressiveness_2", "expressiveness_3", "expressiveness_4", "expressiveness_5"]
        random.shuffle(form_fields)
        return form_fields

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.participant.page_sequence['C']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )

class Public_Self(Page):
    form_model = "player"

    @staticmethod
    def get_form_fields(player: Player):
        form_fields = ["public_self_1", "public_self_2", "public_self_3", "public_self_4", "public_self_5"]
        random.shuffle(form_fields)
        return form_fields

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.participant.page_sequence['D']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )


page_sequence = [Greed_Avoicance, Equity, Expressiveness, Public_Self]
