from otree.api import *
from google.cloud import speech
import os
import io


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = "DG"
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1
    ENDOWMENT = cu(5)
    RULES_TEMPLATE = "dictatorGame/T_Rules.html"
    PRIVACY_TEMPLATE = "dictatorGame/T_Privacy.html"


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
# testing
    test = models.IntegerField(doc="debugging field for testing purposes", blank=True)

# treatment variable (IV) describing the decision modality, i.e. ["Voice", "Text", "Dropdown"]
    interface = models.StringField(doc="treatment variable describing how the dictator communicates his/her decision.")

# Primary Outcome Variable (DV)
    allocation = models.StringField(doc="the share the dictator allocates to the recipient.", blank=True)
    writtenDecision = models.StringField(doc="text Interface: the share the dictator allocates to the recipient.", blank=True)
    spokenDecision = models.StringField(doc="voice Interface: the share the dictator allocates to the recipient.", blank=True)
    selectedDecision = models.StringField(doc="dropdown Interface: the share the dictator allocates to the recipient.", blank=True)

# Store Voice Inputs as Base64 Stings
    decisionBase64 = models.LongStringField(doc="base64 encoded voice input on decision screen.", blank=True)
    check1Base64 = models.LongStringField(doc="first base64 encoded voice input on mic test screen.", blank=True)
    check2Base64 = models.LongStringField(doc="second base64 encoded voice input on mic test screen.", blank=True)
    check3Base64 = models.LongStringField(doc="third base64 encoded voice input on mic test screen.", blank=True)

# Technical Covariates (aka web tracking)
    longitude = models.StringField(doc="the participant's location: longitude.", blank=True)
    latitude = models.StringField(doc="the participant's location: latitude.", blank=True)
    ipAddress = models.StringField(doc="the participant's IP address", blank=True)
    width = models.IntegerField(doc="the participant's screen width.", blank=True)
    height = models.IntegerField(doc="the participant's screen width.", blank=True)
    devicePixelRatio = models.IntegerField(doc="the participant's ratio of pixel sizes.", blank=True)
    userAgent = models.LongStringField(doc="get user agent, i.e. (unreliable) device info.", blank=True)
    recordings = models.IntegerField(doc="counts the number of times a recording was made.", blank=True)




# FUNCTIONS -----
def creating_session(subsession):
    import itertools
    shuffle = itertools.cycle(["Voice", "Text", "Dropdown"])
    for player in subsession.get_players():
        player.interface = next(shuffle)
    print(os.getcwd())


# PAGES -----
class A_Intro(Page):
    pass

class B_MicTest(Page):
    form_model = "player"
    form_fields = ["check1Base64", "check2Base64", "check3Base64"]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )

    @staticmethod
    def js_vars(player: Player):
        return dict(
            template="mic_test",
            allow_replay=True
        )

    @staticmethod
    def live_method(player: Player, data):
        print('the base64 string of ', player.id_in_group, ' is ', len(data), ' characters long.')
        player.test = len(data)
        return {player.id_in_group: len(data)}

class C_Instructions(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        # setting Google credential
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../../ibtanalytics-0ba5cc05ef54.json'
        # create client instance
        client = speech.SpeechClient()

class E_Decision(Page):
    form_model = "player"
    form_fields = ["test", "allocation", "spokenDecision",
                   "longitude", "latitude", "ipAddress", "width", "height", "devicePixelRatio", "userAgent"]


    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )

    @staticmethod
    def js_vars(player: Player):
        return dict(
            template="decision",
            allow_replay=True
        )

    @staticmethod
    def live_method(player: Player, data):
        print('the base64 string of ', player.id_in_group, ' is ', len(data), ' characters long.')
        player.test = len(data)

        # setting Google credential
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../../ibtanalytics-0ba5cc05ef54.json'
        # create client instance
        client = speech.SpeechClient()

        gcs_uri = "gs://cloud-samples-data/speech/brooklyn_bridge.raw"

        # audio = speech.RecognitionAudio(uri=gcs_uri)

        audio = speech.RecognitionAudio(content=data)

        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
            audio_channel_count=1,
            sample_rate_hertz=48000,
            language_code="en-US",
        )

        # Detects speech in the audio file
        response = client.recognize(config=config, audio=audio)
        print(response)

        for result in response.results:
            print("Transcript: {}".format(result.alternatives[0].transcript))

        return {player.id_in_group: len(data)}

class F_Results(Page):

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )

class G_Questionnaire(Page):

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )

class H_Demographics(Page):

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )

class I_Outro(Page):

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect="",
        )


page_sequence = [A_Intro,
                 B_MicTest,
                 C_Instructions,
                 E_Decision,
                 F_Results,
                 G_Questionnaire,
                 H_Demographics,
                 I_Outro]
