# Code Book

The following table shows the variables displayed in the _processed_ data that corresponds to the dictator game.

| processed name              | type | description                                                                     | class     | values                                                  |
|-----------------------------|------|---------------------------------------------------------------------------------|-----------|---------------------------------------------------------|
| session_code                | meta | code of experimental sessions                                                   | character | ['ts95vxj6', 'y9fd8sl8']                                |
| participant_code            | meta | a participant's unique ID; randomly assigned by oTree                           | character | e.g. 'xb94sb1c'                                         |
| participant_interface       | IV   | the interface a participant is exposed to                                       | factor    | [Dropdown, Slider, Text, Voice]                         |
| participant_allowReplay     | IV   | indicates whether a participant was enabled to listen to her voice recording    | boolean   | [TRUE, FALSE]                                           |
| participant_treatment       | IV   | the combination of the two IVs mentioned above                                  | factor    | [Dropdown, Slider, Text, Voice_no_replay, Voice_replay] |
| participant_voice_treatment | IV   | indicates whether a participant was exposed to a voice interface or not         | boolean   | [TRUE, FALSE]                                           |
| dg_recordings               | para | counts the number of times a recording was made                                 | integer   | NA, 1, 2, ...                                           |
| dg_replays                  | para | counts the number of times a recording was replayed                             | integer   | NA, 1, 2, ...                                           |
| dg_allocation               | DV   | the amount the dictator allocates to the recipient                              | integer   | 0, 1, 2, ..., 200                                       |
| dg_writtenDecision          | DV   | Text & Voice interface only: the amount the dictator allocates to the recipient | character | e.g. 'I allocate 50 cents.'                             |
| dg_spokenDecision           | DV   | Voice interface only: the amount the dictator allocates to the recipient        | character | e.g. 'I allocate 50 cents.'                             |