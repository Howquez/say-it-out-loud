from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'outro'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    RULES_TEMPLATE = "dictatorGame/T_Rules.html"
    PRIVACY_TEMPLATE = "dictatorGame/T_Privacy.html"
    PAPERCUPS_TEMPLATE = "dictatorGame/T_PAPERCUPS.html"


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # Feedback
    feedback_1 = models.IntegerField(doc="Please indicate how well you understood the instructions.",
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

    # Privacy
    privacy_1 = models.IntegerField(
        doc="I felt uncomfortable that my use of the user interface can be easily monitored.",
        label="I felt uncomfortable that my use of the user interface can be easily monitored.",
        widget=widgets.RadioSelect,
        choices=[1, 2, 3, 4, 5, 6, 7]
        )
    privacy_2 = models.IntegerField(
        doc="I felt that my use of the user interface makes it easier to invade my privacy.",
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

    image_concerns_1 = models.IntegerField(doc="I did not focus on what other people think of me.",
                                           label="I did not focus on what other people think of me.",
                                           widget=widgets.RadioSelect,
                                           choices=[1, 2, 3, 4, 5, 6, 7]
                                           )

    image_concerns_2 = models.IntegerField(doc="I did not worry about whether anyone could hear what I was saying.",
                                           label="I did not worry about whether anyone could hear what I was saying.",
                                           widget=widgets.RadioSelect,
                                           choices=[1, 2, 3, 4, 5, 6, 7]
                                           )

    image_concerns_3 = models.IntegerField(doc="I was not conscious of how I come across to others.",
                                           label="I was not conscious of how I come across to others.",
                                           widget=widgets.RadioSelect,
                                           choices=[1, 2, 3, 4, 5, 6, 7]
                                           )

    image_concerns_4 = models.IntegerField(doc="I felt like what I was saying was private.",
                                           label="I felt like what I was saying was private.",
                                           widget=widgets.RadioSelect,
                                           choices=[1, 2, 3, 4, 5, 6, 7]
                                           )

    # Emotional state
    guilt = models.IntegerField(doc="Guilty.",
                                label="Guilty",
                                widget=widgets.RadioSelect,
                                choices=[1, 2, 3, 4, 5, 6, 7]
                                )

    proud = models.IntegerField(doc="Proud",
                                label="Proud",
                                widget=widgets.RadioSelect,
                                choices=[1, 2, 3, 4, 5, 6, 7]
                                )

    enthusiastic = models.IntegerField(doc="Enthusiastic",
                                       label="Enthusiastic",
                                       widget=widgets.RadioSelect,
                                       choices=[1, 2, 3, 4, 5, 6, 7]
                                       )

    attentive = models.IntegerField(doc="Attentive",
                                    label="Attentive",
                                    widget=widgets.RadioSelect,
                                    choices=[1, 2, 3, 4, 5, 6, 7]
                                    )

    jittery = models.IntegerField(doc="Jittery",
                                  label="Jittery",
                                  widget=widgets.RadioSelect,
                                  choices=[1, 2, 3, 4, 5, 6, 7]
                                  )

    determined = models.IntegerField(doc="Determined",
                                     label="Determined",
                                     widget=widgets.RadioSelect,
                                     choices=[1, 2, 3, 4, 5, 6, 7]
                                     )

    distressed = models.IntegerField(doc="Distressed",
                                     label="Distressed",
                                     widget=widgets.RadioSelect,
                                     choices=[1, 2, 3, 4, 5, 6, 7]
                                     )

    scared = models.IntegerField(doc="Scared",
                                 label="Scared",
                                 widget=widgets.RadioSelect,
                                 choices=[1, 2, 3, 4, 5, 6, 7]
                                 )

    upset = models.IntegerField(doc="Upset",
                                label="Upset",
                                widget=widgets.RadioSelect,
                                choices=[1, 2, 3, 4, 5, 6, 7]
                                )

    nervous = models.IntegerField(doc="Nervous",
                                  label="Nervous",
                                  widget=widgets.RadioSelect,
                                  choices=[1, 2, 3, 4, 5, 6, 7]
                                  )

    ashamed = models.IntegerField(doc="Ashamed",
                                  label="Ashamed",
                                  widget=widgets.RadioSelect,
                                  choices=[1, 2, 3, 4, 5, 6, 7]
                                  )

    hostile = models.IntegerField(doc="Hostile",
                                  label="Hostile",
                                  widget=widgets.RadioSelect,
                                  choices=[1, 2, 3, 4, 5, 6, 7]
                                  )

    strong = models.IntegerField(doc="Strong",
                                 label="Strong",
                                 widget=widgets.RadioSelect,
                                 choices=[1, 2, 3, 4, 5, 6, 7]
                                 )

    alert = models.IntegerField(doc="Alert",
                                label="Alert",
                                widget=widgets.RadioSelect,
                                choices=[1, 2, 3, 4, 5, 6, 7]
                                )

    irritable = models.IntegerField(doc="Irritable",
                                    label="Irritable",
                                    widget=widgets.RadioSelect,
                                    choices=[1, 2, 3, 4, 5, 6, 7]
                                    )

    active = models.IntegerField(doc="Active",
                                 label="Active",
                                 widget=widgets.RadioSelect,
                                 choices=[1, 2, 3, 4, 5, 6, 7]
                                 )

    excited = models.IntegerField(doc="Excited",
                                  label="Excited",
                                  widget=widgets.RadioSelect,
                                  choices=[1, 2, 3, 4, 5, 6, 7]
                                  )

    interested = models.IntegerField(doc="Interested",
                                     label="Interested",
                                     widget=widgets.RadioSelect,
                                     choices=[1, 2, 3, 4, 5, 6, 7]
                                     )

    afraid = models.IntegerField(doc="Afraid",
                                 label="Afraid",
                                 widget=widgets.RadioSelect,
                                 choices=[1, 2, 3, 4, 5, 6, 7]
                                 )

    inspired = models.IntegerField(doc="Inspired",
                                   label="Inspired",
                                   widget=widgets.RadioSelect,
                                   choices=[1, 2, 3, 4, 5, 6, 7]
                                   )

# Interface
    interface_1 = models.IntegerField(doc="Overall, the decision's interface worked very well technically.",
                                      label="Overall, the decision's interface worked very well technically.",
                                      widget=widgets.RadioSelect,
                                      choices=[1, 2, 3, 4, 5, 6, 7]
                                      )

    interface_2 = models.IntegerField(doc="Visually, the decision's interface resembled other interfaces I think highly of.",
                                      label="Visually, the decision's interface resembled other interfaces I think highly of.",
                                      widget=widgets.RadioSelect,
                                      choices=[1, 2, 3, 4, 5, 6, 7]
                                      )

    interface_3 = models.IntegerField(doc="The decision's interface was simple to navigate.",
                                      label="The decision's interface was simple to navigate.",
                                      widget=widgets.RadioSelect,
                                      choices=[1, 2, 3, 4, 5, 6, 7]
                                      )

    interface_4 = models.IntegerField(doc="With this interface, it was very easy to submit my decision.",
                                      label="With this interface, it was very easy to submit my decision.",
                                      widget=widgets.RadioSelect,
                                      choices=[1, 2, 3, 4, 5, 6, 7]
                                      )



# PAGES
class A_Feedback(Page):
    form_model = "player"
    form_fields = ["feedback_1", "feedback_2", "feedback_3"]


    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )


class B_Location(Page):
    form_model = "player"
    form_fields = ["location"]


    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )


class B_Privacy(Page):
    form_model = "player"
    form_fields = ["privacy_1", "privacy_2", "privacy_3"]


    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )


class C_Image(Page):
    form_model = "player"
    form_fields = [# "location",
                   "image_concerns_1", "image_concerns_2", "image_concerns_3", "image_concerns_4"]


    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )



class D_Emotions(Page):
    form_model = "player"
    form_fields = ["guilt", "proud", "enthusiastic", "jittery", "determined", "distressed", "scared",
                   "upset", "nervous", "ashamed", "hostile", "strong", "alert", "irritable", "active",
                   "excited", "interested", "afraid", "inspired"]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )


class E_Interface(Page):
    form_model = "player"
    form_fields = ["interface_1", "interface_2", "interface_3", "interface_4"]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )



class E_Demographics(Page):
    form_model = "player"
    form_fields = ["age", "gender", "education", "income"]


    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )



class F_Debriefing(Page):
    form_model = "player"
    form_fields = []

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )



page_sequence = [A_Feedback, B_Privacy, B_Location, C_Image, D_Emotions, E_Interface, E_Demographics, F_Debriefing]
