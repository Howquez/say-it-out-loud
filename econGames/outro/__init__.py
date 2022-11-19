from otree.api import *
import random

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'outro'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    RULES_TEMPLATE = "dictatorGame/T_Rules.html"
    PRIVACY_TEMPLATE = "dictatorGame/T_Privacy.html"
    MEDIATORS_TEMPLATE = "mediators/T_Mediators.html"

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
# completed the survey
    completed_survey = models.BooleanField(
        doc="True as soon as participants submit Feedback page",
        initial=False
    )

# PANAS scale
    guilt = models.IntegerField(
        doc="Guilty.",
        label="Guilty",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7])

    proud = models.IntegerField(
        doc="Proud",
        label="Proud",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7])

    enthusiastic = models.IntegerField(
        doc="Enthusiastic",
        label="Enthusiastic",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7])

    attentive = models.IntegerField(
        doc="Attentive",
        label="Attentive",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7])

    jittery = models.IntegerField(
        doc="Jittery",
        label="Jittery",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7])

    determined = models.IntegerField(
        doc="Determined",
        label="Determined",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7])

    distressed = models.IntegerField(
        doc="Distressed",
        label="Distressed",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7])

    scared = models.IntegerField(
        doc="Scared",
        label="Scared",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7])

    upset = models.IntegerField(
        doc="Upset",
        label="Upset",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7])

    nervous = models.IntegerField(
        doc="Nervous",
        label="Nervous",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7])

    ashamed = models.IntegerField(
        doc="Ashamed",
        label="Ashamed",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7])

    hostile = models.IntegerField(
        doc="Hostile",
        label="Hostile",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7])

    strong = models.IntegerField(
        doc="Strong",
        label="Strong",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7])

    alert = models.IntegerField(
        doc="Alert",
        label="Alert",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7])

    irritable = models.IntegerField(
        doc="Irritable",
        label="Irritable",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7])

    active = models.IntegerField(
        doc="Active",
        label="Active",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7])

    excited = models.IntegerField(
        doc="Excited",
        label="Excited",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7])

    interested = models.IntegerField(
        doc="Interested",
        label="Interested",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7])

    afraid = models.IntegerField(
        doc="Afraid",
        label="Afraid",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7])

    inspired = models.IntegerField(
        doc="Inspired",
        label="Inspired",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7])

# Interface
    interface_1 = models.IntegerField(
        doc="Overall, this interface worked very well technically.",
        label="Overall, this interface worked very well technically.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7])

    interface_2 = models.IntegerField(
        doc="Visually, this interface resembled other interfaces I think highly of.",
        label="Visually, this interface resembled other interfaces I think highly of.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7])

    interface_3 = models.IntegerField(
        doc="this interface was simple to navigate.",
        label="The decision's interface was simple to navigate.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7])

    interface_4 = models.IntegerField(
        doc="With this interface, it was very easy to submit my decision.",
        label="With this interface, it was very easy to submit my decision.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7])

    interface_5 = models.IntegerField(
        doc="The interface allowed me to efficiently communicate my decision.",
        label="The interface allowed me to efficiently communicate my decision.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7])

    interface_6 = models.IntegerField(
        doc="The user interface was somewhat intimidating to me.",
        label="The user interface was somewhat intimidating to me.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7])

    interface_7 = models.IntegerField(
        doc="It scared me to think that I could provide a wrong answer using the user interface.",
        label="It scared me to think that I could provide a wrong answer using the user interface.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7])


# Situational covariates
    location = models.IntegerField(
        label="Where were you when you were while making the allocation decision in the current study?",
        blank=False,
        widget=widgets.RadioSelect,
        choices=[
            [1, "In a public space (e.g., coffee shop) near other people."],
            [2, "In a public space where NO ONE was around."],
            [3, "In a personal space (e.g., home or office) near other people."],
            [4, "In a personal space (e.g., home or office) where NO ONE was around."],
        ]
    )

# Technical Self Reports
    device = models.IntegerField(
        label="What device are you using to complete this survey?",
        blank=False,
        choices=[
            [1, "Mobile Phone"],
            [2, "Tablet"],
            [3, "Laptop"],
            [4, "Desktop Computer"],
        ]
    )

    operating_system = models.IntegerField(
        label="What operating system does your device use?",
        blank=False,
        choices=[
            [1, "Mac OS or iOS"],
            [2, "Android"],
            [3, "Windows"],
            [4, "Other"],
        ]
    )

    browser = models.IntegerField(
        label="Which browser did you use to complete this study?",
        blank=False,
        choices=[
            [1, "Chrome"],
            [2, "Safari"],
            [3, "Firefox"],
            [4, "Internet Explorer"],
            [5, "Microsoft Edge"],
            [6, "Other"]
        ]
    )

    microphone = models.IntegerField(
        label="Which kind of microphone have you been using during the task?",
        blank=False,
        choices=[
            [1, "Built-in microphone"],
            [2, "External microphone"],
            [3, "Other"],
        ]
    )


# Demographics
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
        label="What is the highest level of education you achieved?",
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
        label="What is your total household income per year?",
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

# Hypothesis
    hypothesis = models.LongStringField(
        doc="What do you think was the hypothesis of this research?",
        label="What do you think was the hypothesis of this research?",
        blank=False)

# Feedback
    feedback_1 = models.IntegerField(
        doc="Please indicate how well you understood the instructions.",
        label="Please indicate how well you understood the instructions.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7],
        blank=False)

    feedback_2 = models.LongStringField(
        doc="Was there anything that surprised you, that is, anything you expected to be different?",
        lable="Was there anything that surprised you, that is, anything you expected to be different?",
        blank=False)

    feedback_3 = models.LongStringField(
        doc="Do you have any suggestions how we can improve the instructions to make them more comprehensible?",
        lable="Do you have any suggestions how we can improve the instructions to make them more comprehensible?",
        blank=False)


# PAGES
class Interface(Page):
    form_model = "player"

    @staticmethod
    def get_form_fields(player: Player):
        form_fields = ["interface_1", "interface_2", "interface_3", "interface_4", "interface_5", "interface_6", "interface_7"]
        random.shuffle(form_fields)
        return form_fields

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )

class Panas(Page):
    form_model = "player"

    @staticmethod
    def get_form_fields(player: Player):
        form_fields = ["guilt", "proud", "enthusiastic", "jittery", "determined", "distressed", "scared",
                       "upset", "nervous", "ashamed", "hostile", "strong", "alert", "irritable", "active",
                       "excited", "interested", "afraid", "inspired"]
        random.shuffle(form_fields)
        return form_fields

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )

class Location(Page):
    form_model = "player"
    form_fields = ["location"]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )

class Technical(Page):
    form_model = "player"

    def get_form_fields(player: Player):
        form_fields = ["device", "browser", "operating_system", "microphone"]
        random.shuffle(form_fields)
        return form_fields

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )

class Feedback(Page):
    form_model = "player"
    form_fields = ["feedback_1", "feedback_2", "feedback_3"]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )


class Demographics(Page):
    form_model = "player"
    form_fields = ["age", "gender", "education", "income"]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )


class Hypothesis(Page):
    form_model = "player"
    form_fields = ["hypothesis"]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )


class Feedback(Page):
    form_model = "player"
    form_fields = ["feedback_1", "feedback_2", "feedback_3", "completed_survey"]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.participant.finished = True
        player.completed_survey = player.participant.finished
        player.session.prolific_completion_url = "https://www.ibt.unisg.ch/"


class Debriefing(Page):
    form_model = "player"

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )


page_sequence = [Interface, Panas, Location, Technical, Demographics, Hypothesis, Feedback, Debriefing]
