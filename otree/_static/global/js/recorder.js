console.log("recorder ready!")
console.log("copied from https://towardsdev.com/capture-audio-in-browser-with-javascript-27d83ec9aa67")

// consider browser compatibility:
// https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder#browser_compatibility
// also take a look at this discussion here https://github.com/0x006F/react-media-recorder/issues/31

var recordings = 0

// collect DOMs
const display = document.querySelector('.display')
const replay = document.querySelector('.replay')
const controllerWrapper = document.querySelector('.controllers')

const State = ['Initial', 'Record', 'Revision']
let stateIndex = 0
let mediaRecorder, chunks = [], audioURL = ''

// mediaRecorder setup for audio
if(navigator.mediaDevices && navigator.mediaDevices.getUserMedia){
    console.log('mediaDevices supported..')

    navigator.mediaDevices.getUserMedia({
        audio: true
    }).then(stream => {
        mediaRecorder = new MediaRecorder(stream)

        mediaRecorder.ondataavailable = (e) => {
            chunks.push(e.data)
        }

        mediaRecorder.onstop = () => {
            const blob = new Blob(chunks, {'type': 'audio/ogg; codecs=opus'})
            chunks = []
            audioURL = window.URL.createObjectURL(blob)
            // document.querySelector('audio').src = audioURL

        }
    }).catch(error => {
        console.log('Following error has occured : ',error)
    })
}else{
    stateIndex = ''
    application(stateIndex)
}

const clearDisplay = () => {
    display.textContent = ''
    replay.textContent = ''
}

const clearControls = () => {
    controllerWrapper.textContent = ''
}

const voiceRecording = () => {
    stateIndex = 1
    mediaRecorder.start()
    application(stateIndex)
}

const stopRecording = () => {
    stateIndex = 2
    mediaRecorder.stop()
    application(stateIndex)
}

const downloadAudio = () => {
    const downloadLink = document.createElement('a')
    downloadLink.href = audioURL
    downloadLink.setAttribute('download', 'audio')
    downloadLink.click()
}

const addButton = (id, funString, text, color, icon) => {
    const btn = document.createElement('button')
    btn.id = id
    btn.setAttribute('onclick', funString)
    btn.textContent = text
    btn.type = "button"
    btn.className = "btn m-0 w-100 btn-outline-" + color + " " + icon
    controllerWrapper.append(btn)
}

const addMessage = (text) => {
    const msg = document.createElement('p')
    msg.textContent = text
    msg.className = "text-secondary"
    display.append(msg)
}

const addAudio = () => {
    const audio = document.createElement('audio')
    audio.controls = true
    audio.src = audioURL
    const note = document.createElement('small')
    note.textContent = "You can listen to your recording above to ensure a sufficient audioquality."
    note.className = "text-secondary mb-5"
    const lineBreak = document.createElement('br')
    replay.append(audio)
    replay.append(lineBreak)
    replay.append(note)
}

const application = (index) => {
    switch (State[index]) {
        case 'Initial':
            clearDisplay()
            clearControls()

            addMessage('Press the left button to start recording your decision and say "I want to transfer x point(s)."')
            addButton('record', 'voiceRecording()', 'Start Recording', "success") //, "bi bi-record-fill")
            break;

        case 'Record':
            clearDisplay()
            clearControls()

            addMessage('Recording...')
            addButton('stop', 'stopRecording()', 'Stop Recording', "danger", "bi bi-stop-fill")
            document.getElementById("submit_button").disabled = true;
            break

        case 'Revision':
            clearControls()
            clearDisplay()
            recordings += 1

            // addAudio()
            addMessage('Submit or record again saying "I want to transfer x point(s)."')
            // addButton('download', 'downloadAudio()', 'Dwnload Audio', "primary")
            addButton('record', 'voiceRecording()', 'Record Again', "success", "bi bi-arrow-repeat")
            document.getElementById("submit_button").disabled = false;
            break

        default:
            clearControls()
            clearDisplay()

            addMessage('Your browser does not support mediaDevices')
            break;
    }

}

application(stateIndex)