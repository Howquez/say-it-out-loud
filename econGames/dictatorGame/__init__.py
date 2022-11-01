from otree.api import *
import itertools
from google.cloud import speech
import os
import io
from word2number import w2n


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = "DG"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 3
    ENDOWMENT = cu(5)
    RULES_TEMPLATE = "dictatorGame/T_Rules.html"
    PRIVACY_TEMPLATE = "dictatorGame/T_Privacy.html"
    PAPERCUPS_TEMPLATE = __name__ + '/T_PAPERCUPS.html'



class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
# testing
    test = models.IntegerField(doc="debugging field for testing purposes", blank=True)

# treatment variables (IV) describing the decision modality, i.e. ["Voice", "Text", "Dropdown"]
    interface = models.StringField(doc="treatment variable describing how the dictator communicates his/her decision.")
    allowReplay = models.BooleanField(doc="treatment variable describing whether participants were allowed to listen to their recordings.",
                                      initial=False)

# Primary Outcome Variable (DV)
    allocation = models.IntegerField(doc="the share the dictator allocates to the recipient.", blank=True)
    writtenDecision = models.StringField(doc="text Interface: the share the dictator allocates to the recipient.", blank=True)
    spokenDecision = models.LongStringField(doc="voice Interface: the share the dictator allocates to the recipient.", blank=True)
    spokenDecisionBackup = models.LongStringField(doc="voice Interface: backup decision", blank=True)
    sliderDecision = models.StringField(doc="slider Interface: the share the dictator allocates to the recipient.", blank=True)
    selectedDecision = models.IntegerField(doc="dropdown Interface: the share the dictator allocates to the recipient.",
                                           blank=True,
                                           choices=list(range(0, int(C.ENDOWMENT)*100+1)))

# Store Voice Inputs as Base64 Stings
    decisionBase64 = models.LongStringField(doc="base64 encoded voice input on decision screen.", blank=True)
    checkBase64 = models.LongStringField(doc="base64 encoded voice input on mic test screens.", blank=True)

# Technical Covariates (aka web tracking)
    longitude = models.StringField(doc="the participant's location: longitude.", blank=True)
    latitude = models.StringField(doc="the participant's location: latitude.", blank=True)
    ipAddress = models.StringField(doc="the participant's IP address", blank=True)
    width = models.IntegerField(doc="the participant's screen width.", blank=True)
    height = models.IntegerField(doc="the participant's screen width.", blank=True)
    devicePixelRatio = models.IntegerField(doc="the participant's ratio of pixel sizes.", blank=True)
    userAgent = models.LongStringField(doc="get user agent, i.e. (unreliable) device info.", blank=True)
    recordings = models.IntegerField(doc="counts the number of times a recording was made.", blank=True)
    replays = models.IntegerField(doc="counts the number of times a recording was replayed.", blank=True)
    privacy_time = models.FloatField(doc="counts the number of seconds the privacy statement was opened.", blank=True)

# Questionnaire
    privacy_1 = models.IntegerField(doc="I felt uncomfortable that my use of the user interface can be easily monitored.",
                                    label="I felt uncomfortable that my use of the user interface can be easily monitored.",
                                    widget=widgets.RadioSelect,
                                    choices=[1, 2, 3, 4, 5, 6, 7]
                                    )
    privacy_2 = models.IntegerField(doc="I felt that my use of the user interface makes it easier to invade my privacy.",
                                    label="I felt that my use of the user interface makes it easier to invade my privacy.",
                                    widget=widgets.RadioSelect,
                                    choices=[1, 2, 3, 4, 5, 6, 7]
                                    )
    privacy_3 = models.IntegerField(doc="I felt that my privacy could be violated by an external organization tracking my activities using the user interface.",
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


# FUNCTIONS -----
def creating_session(subsession):
    shuffle = itertools.cycle(["Voice", "Voice", "Text", "Dropdown", "Slider"])
    replay  = itertools.cycle([True, False])
    for player in subsession.get_players():
        player.interface = next(shuffle)
        if player.interface == "Voice":
            player.allowReplay = next(replay)

def set_payoffs(group: Group):
    for p in group.get_players():
        allocated = 2.3
        received  = 1
        p.payoff  = C.ENDOWMENT - allocated + received

def transcribe(player: Player):
    if player.interface == "Text":
        try:
            allocation = int(w2n.word_to_num(player.writtenDecision))
        except:
            allocation = 9999
        print(allocation)
        player.allocation = allocation
    if player.interface == "Dropdown":
        player.allocation = player.selectedDecision
    if player.interface == "Slider":
        player.allocation = player.sliderDecision


# PAGES -----
class A_Intro(Page):
    form_model = "player"
    form_fields = ["privacy_time"]

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1



class B_MicTest(Page):
    form_model = "player"
    form_fields = ["checkBase64", "recordings",
                   "longitude", "latitude", "ipAddress", "width", "height", "devicePixelRatio", "userAgent"]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )

    @staticmethod
    def js_vars(player: Player):
        return dict(
            round_number=player.round_number,
            template="mic_test",
            allow_replay=True
        )

    @staticmethod
    def live_method(player: Player, data):
        # print('the base64 string of ', player.id_in_group, ' is ', len(data), ' characters long.')
        player.test = len(data)
        return {player.id_in_group: len(data)}




class C_Instructions(Page):

    @staticmethod
    def is_displayed(player):
        return player.round_number == 3

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )




class E_Decision(Page):
    form_model = "player"
    form_fields = ["test", "allocation", "spokenDecision", "spokenDecisionBackup", "writtenDecision", "selectedDecision", "sliderDecision",
                   "recordings", "replays",
                   "longitude", "latitude", "ipAddress", "width", "height", "devicePixelRatio", "userAgent"]

    @staticmethod
    def is_displayed(player):
        return player.round_number == 3

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )

    @staticmethod
    def js_vars(player: Player):
        return dict(
            template="decision",
            allow_replay=player.allowReplay
        )

    @staticmethod
    def live_method(player: Player, data):
        print('the base64 string of ', player.id_in_group, ' is ', len(data), ' characters long.')
        player.test = len(data)

        # # setting Google credential
        # os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../../ibtanalytics-0ba5cc05ef54.json'
        # # create client instance
        # client = speech.SpeechClient()
        #
        # # Google's example
        # # gcs_uri = "gs://cloud-samples-data/speech/brooklyn_bridge.raw"
        # # audio = speech.RecognitionAudio(uri=gcs_uri)
        #
        # audio = speech.RecognitionAudio(content=data)
        #
        # config = speech.RecognitionConfig(
        #     encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
        #     audio_channel_count=1,
        #     sample_rate_hertz=48000,
        #     language_code="en-US",
        # )
        #
        # # Detects speech in the audio file
        # response = client.recognize(config=config, audio=audio)
        # print(response)
        # for result in response.results:
        #     print("Transcript: {}".format(result.alternatives[0].transcript))

        return {player.id_in_group: len(data)}

    @staticmethod
    def before_next_page(player, timeout_happened):
        transcribe(player)
        # set_payoffs()

class F_Results(Page):

    @staticmethod
    def is_displayed(player):
        return player.round_number == 3

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )

class G_Questionnaire(Page):
    form_model = "player"
    form_fields = ["privacy_1", "privacy_2", "privacy_3"]

    @staticmethod
    def is_displayed(player):
        return player.round_number == 3

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
        return player.round_number == 3

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )

class I_Outro(Page):

    @staticmethod
    def is_displayed(player):
        return player.round_number == 3

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )


page_sequence = [A_Intro,
                 B_MicTest,
                 C_Instructions,
                 E_Decision,
                 # F_Results,
                 G_Questionnaire,
                 H_Demographics,
                 I_Outro]
