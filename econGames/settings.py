from os import environ

SESSION_CONFIGS = [
    dict(
        name="Dictator_Game",
        app_sequence=["dictatorGame", "mediators", "moderators", "outro"],
        num_demo_participants=5,
    ),
    dict(
        name='Testing',
        app_sequence=["dictatorGame", "outro"],
        num_demo_participants=10,
    ),
    dict(
        name='Social_media_feed',
        app_sequence=['feed'],
        num_demo_participants=3,
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=1.00, doc=""
)

PARTICIPANT_FIELDS = ["interface", "allowReplay", "page_sequence", "finished"]
SESSION_FIELDS = ["ENDOWMENT", "prolific_completion_url"]

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = "en"

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = "USD"
USE_POINTS = False

ADMIN_USERNAME = "admin"
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get("OTREE_ADMIN_PASSWORD")

DEMO_PAGE_INTRO_HTML = """ Hej! """

SECRET_KEY = '8754845048400'
