// vars from oTree -----
    let participant_label = js_vars.participant_label;
    let template = js_vars.template;
    let allow_replay = js_vars.allow_replay;

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
    var inputField = document.getElementById("spokenDecision");

// Based on template, choose the message to be read out loud
    var decision = "'I allocate [...] cents.'";
    var counting = "'1, 2, 3, [...], 8, 9, 10'";
    var blue = "'The blue spot is on the key again.'";
    var mama = "'My mama makes lemon jam.'";
    var peter = "'Peter will keep at the peak.'";
    var msg;

    if (template == "mic_test"){
        msg = counting;
    } else if (template == "decision"){
        msg = decision;
    }


// template specifics (comprehension vs decision screen) -----
    if(template == "mic_test"){
        inputField = document.getElementById("check1Base64")
        readAloud.textContent = '"I have read and understand the instructions."'
    }else{
        readAloud.textContent = msg;
    }