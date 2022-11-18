from otree.api import *
import random

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'med'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    MEDIATORS_TEMPLATE = "mediators/T_Mediators.html"


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
# Empathy
    empathy_1 = models.IntegerField(
        doc="I tried to imagine how the other person feels about my decisions.",
        label="I tried to imagine how the other person feels about my decisions.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7],
        blank=False)

    empathy_2 = models.IntegerField(
        doc="I imagined how the other person felt during this task.",
        label="I imagined how the other person felt during this task.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7],
        blank=False)

    empathy_3 = models.IntegerField(
        doc="I wondered how I would feel if I were the receiver in this task.",
        label="I wondered how I would feel if I were the receiver in this task.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7],
        blank=False)

# Image
    image_1 = models.IntegerField(
        doc="I did not worry about whether anyone could hear what I was saying.",
        label="I did not worry about whether anyone could hear what I was saying.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7],
        blank=False)

    image_2 = models.IntegerField(
        doc="I did not focus on what other people think of me.",
        label="I did not focus on what other people think of me.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7],
        blank=False)

    image_3 = models.IntegerField(
        doc="I was not conscious of how I come across to others.",
        label="I was not conscious of how I come across to others.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7],
        blank=False)

    image_4 = models.IntegerField(
        doc="I felt like what I was saying was private.",
        label="I felt like what I was saying was private.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7],
        blank=False)

    # Concern for Face
    face_concern_1 = models.IntegerField(
        doc="I cared about others' attitudes toward me.",
        label="I cared about others' attitudes toward me.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7],
        blank=False)

    face_concern_2 = models.IntegerField(
        doc="I cared about getting criticized or praised from others.",
        label="I cared about getting criticized or praised from others.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7],
        blank=False)

# Thought of Focus on Self
    self_focus_1 = models.IntegerField(
        doc="I thought just about myself.",
        label="I thought just about myself.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7],
        blank=False)

    self_focus_2 = models.IntegerField(
        doc="The task encouraged me to focus on myself.",
        label="The task encouraged me to focus on myself.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7],
        blank=False)

    self_focus_3 = models.IntegerField(
        doc="My thoughts were focused just on me.",
        label="My thoughts were focused just on me.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7],
        blank=False)

# Privacy
    privacy_1 = models.IntegerField(
        doc="I felt uncomfortable that this user interface can be easily monitored.",
        label="I felt uncomfortable that my use of the user interface can be easily monitored.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7]
    )
    privacy_2 = models.IntegerField(
        doc="I felt that this interface makes it easier to invade my privacy.",
        label="I felt that my use of the user interface makes it easier to invade my privacy.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7]
    )
    privacy_3 = models.IntegerField(
        doc="I felt that my privacy could be violated by an external organization tracking my activities using the user interface.",
        label="I felt that my privacy could be violated by an external organization tracking my activities using the user interface.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7]
    )

# Distribution
    fair = models.IntegerField(
        doc="My distribution toward the other person felt...",
        label="unfair / fair",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7]
    )

    right = models.IntegerField(
        doc="My distribution toward the other person felt...",
        label="wrong / right",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7]
    )

    reasonable = models.IntegerField(
        doc="My distribution toward the other person felt...",
        label="unreasonable / reasonable",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7]
    )


# PAGES

class Empathy(Page):
    form_model = "player"

    @staticmethod
    def get_form_fields(player: Player):
        form_fields = ["empathy_1", "empathy_2", "empathy_3"]
        random.shuffle(form_fields)
        return form_fields

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )

class Image(Page):
    form_model = "player"

    @staticmethod
    def get_form_fields(player: Player):
        form_fields = ["image_1", "image_2", "image_3", "image_4"]
        random.shuffle(form_fields)
        return form_fields

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )

class Face_Concern(Page):
    form_model = "player"

    @staticmethod
    def get_form_fields(player: Player):
        form_fields = ["face_concern_1", "face_concern_2"]
        random.shuffle(form_fields)
        return form_fields

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )

class Self_Focus(Page):
    form_model = "player"

    @staticmethod
    def get_form_fields(player: Player):
        form_fields = ["self_focus_1", "self_focus_2", "self_focus_3"]
        random.shuffle(form_fields)
        return form_fields

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )

class Privacy(Page):
    form_model = "player"

    @staticmethod
    def get_form_fields(player: Player):
        form_fields = ["privacy_1", "privacy_2", "privacy_3"]
        random.shuffle(form_fields)
        return form_fields

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )

class Distribution(Page):
    form_model = "player"
    form_fields = ["fair", "right", "reasonable"]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )


page_sequence = [Distribution,
                 Empathy, Image, Face_Concern, Self_Focus, Privacy]
