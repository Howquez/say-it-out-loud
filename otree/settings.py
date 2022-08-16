from os import environ

SESSION_CONFIGS = [
    # dict(
    #     name='beta',
    #     display_name="Dictator_Game",
    #     app_sequence=["A_Intro", "B_Game", "C_Outro"],
    #     num_demo_participants=4,
    # ),
    dict(
        name='slim',
        display_name="Charity",
        app_sequence=["D_Charity"],
        num_demo_participants=2,
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=1.00, doc=""
)


ROOMS = [
    dict(
        name='Session_1',
        display_name='Session 1',
        participant_label_file='_rooms/Session_1.txt',
        use_secure_urls=True
    ),
]

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '4986426003509'
