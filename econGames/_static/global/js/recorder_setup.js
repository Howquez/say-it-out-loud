// vars from oTree -----
    let participant_label = js_vars.participant_label;
    let template = js_vars.template;
    let allow_replay = js_vars.allow_replay;
    let round_number = js_vars.round_number;

// collect DOMs
    // pick statement to be read out loud
    const readAloud = document.querySelector('.readAloud');

    // Identify divs to display recorder's properties
    const display = document.querySelector('.display');
    const controllerWrapper = document.querySelector('.controllers');
    const replay = document.querySelector('.replay');

    // state variables
    const State = ['Initial', 'Record', 'Revision'];
    let mediaRecorder, chunks = [], audioURL = '', blob;
    let stateIndex = 0;

    // Misc
    var recordings = 0;
    var replays = 0;
    var inputField = document.getElementById("spokenDecision");

// Based on template, choose the message to be read out loud
    var decision = "'I allocate [...] cents.'";
    var counting = "'1, 2, 3, 4, 5, 6, 7, 8, 9, 10'";
    var blue = "'The blue spot is on the key again.'";
    var mama = "'My mama makes lemon jam.'";
    var peter = "'Peter will keep at the peak.'";
    var msg;

    if (template == "mic_test"){
        msg = [counting, blue, mama][round_number - 1];
    } else if (template == "decision"){
        msg = decision;
    }


// template specifics (comprehension vs decision screen) -----
    if(template == "mic_test"){
        inputField = document.getElementById("checkBase64")
    }

    readAloud.textContent = msg;