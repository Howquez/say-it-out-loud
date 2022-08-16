from otree.api import Currency as c, currency_range, expect, Bot
from . import *
import random

class PlayerBot(Bot):
    def play_round(self):

        if self.round_number == 1:
            yield A_Intro
            yield B_Instructions

            baseline_voice_file = open("_static/global/base64/baseline.txt")
            baseline_voice = baseline_voice_file.read()
            baseline_voice_file.close
            yield D_Comprehension, dict(comprehensionAudio=baseline_voice,
                                        recordings=random.randint(1, 4))

        if self.player.voice_interface:
            decision_voice_file = open("_static/global/base64/voice.txt")
            decision_voice = baseline_voice_file.read()
            decision_voice_file.close
            yield E_Decision, dict(voiceBase64=decision_voice,
                                   recordings=1,
                                   longitude="User denied the request for Geolocation.",
                                   latitude="User denied the request for Geolocation.",
                                   ipAddress="130.82.29.23",
                                   width="414",
                                   height="896",
                                   devicePixelRatio=1,
                                   userAgent="I'm a bot")
        else:
            yield E_Decision, dict(share=random.randint(0, 10),
                                   recordings=1,
                                   longitude="User denied the request for Geolocation.",
                                   latitude="User denied the request for Geolocation.",
                                   ipAddress="130.82.29.23",
                                   width="414",
                                   height="896",
                                   devicePixelRatio=1,
                                   userAgent="I'm a bot")

        if self.round_number == C.NUM_ROUNDS:
            yield G_Questionnaire, dict(comp_1=random.randint(1, 5),
                                        comp_2="I'm a bot",
                                        comp_3="I'm a bot")

            yield H_Demographics, dict(age=random.randint(18, 99),
                                       gender=random.randint(1, 3),
                                       education=random.randint(1, 8),
                                       income=random.randint(1, 8))

            yield I_Outro
