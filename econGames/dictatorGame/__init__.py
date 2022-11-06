from otree.api import *
import itertools
# from google.cloud import speech
# import os
# import io
import re
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
    sliderDecision = models.IntegerField(doc="slider Interface: the share the dictator allocates to the recipient.", blank=True)
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
    instructions_time = models.FloatField(doc="counts the number of seconds the instructions were reviewed.", blank=True)


# FUNCTIONS -----
def creating_session(subsession):
    shuffle = itertools.cycle(["Voice", "Voice", "Text", "Dropdown", "Slider"])
    replay  = itertools.cycle([True, False])
    for player in subsession.get_players():
        player.interface = next(shuffle)
        if player.interface == "Voice":
            player.allowReplay = next(replay)
        player.session.ENDOWMENT = C.ENDOWMENT
        player.participant.interface = player.interface
        player.participant.allowReplay = player.allowReplay

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
            try:
                allocation = int(re.sub("\D", "", player.writtenDecision))
            except:
                allocation = 9999
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

    @staticmethod
    def js_vars(player: Player):
        return dict(
            template="intro",
        )



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
                   "recordings", "replays", "instructions_time",
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


page_sequence = [A_Intro,
                 B_MicTest,
                 C_Instructions,
                 E_Decision]
