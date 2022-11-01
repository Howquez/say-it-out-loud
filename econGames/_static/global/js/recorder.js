console.log("recorder ready!")

// Sources: https://towardsdev.com/capture-audio-in-browser-with-javascript-27d83ec9aa67
// and      https://github.com/duketemon/web-speech-recorder/blob/master/source/static/index.html

// consider browser compatibility:
// https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder#browser_compatibility
// also take a look at this discussion here https://github.com/0x006F/react-media-recorder/issues/31


// mediaRecorder setup for audio -----
    if(navigator.mediaDevices && navigator.mediaDevices.getUserMedia){
        console.log('mediaDevices supported..')

        navigator.mediaDevices.getUserMedia({
            audio: true
        }).then(stream => {
            // see for more options: https://stackoverflow.com/a/53597051
            mediaRecorder = new MediaRecorder(stream, {
                type: "audio"
            })

            mediaRecorder.ondataavailable = (e) => {
                chunks.push(e.data)
            }

            mediaRecorder.onstop = () => {
                blob = new Blob(chunks, {type: 'audio/wav; codecs=0'});
                chunks = []
                audioURL = window.URL.createObjectURL(blob)
                // sendData(blob);
                if(allow_replay){
                    document.querySelector('audio').src = audioURL
                    }

                // encode to base64 and
                var reader = new window.FileReader();
                reader.readAsDataURL(blob);
                reader.onloadend = function() {
                   base64 = reader.result;
                   base64 = base64.split(',')[1];
                   inputField.value += ' RECORDING_' + recordings + ': ' + base64;
                   // inputField.value = inputField.value.substring(0, 100000);
                   console.log("inputField " + inputField.value.substring(1, 42));
                   liveSend(base64);
                }
            }


        }).catch(error => {
            console.log('Following error has occured : ',error)
        })
    }else{
        stateIndex = ''
        application(stateIndex)
    }


// frontend operations -----
    const clearDisplay = () => {
        display.textContent = ''
        if(allow_replay){
            replay.textContent = ''
            }
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
        msg.className = "text-dark"
        display.append(msg)
    }

    const addAudio = () => {
        const audio = document.createElement('audio')
        audio.controls = true
        audio.src = audioURL
        audio.className = "mt-3"
        audio.id = "audio_controls"

        if(allow_replay){
            replay.append(audio);
            audio.addEventListener('ended', function () {
                replays += 1
                document.getElementById("replays").value = replays},
                false);
        }
    }

    const application = (index) => {
        switch (State[index]) {
            case 'Initial':
                clearDisplay()
                clearControls()

                addMessage('Press the left button to start recording your decision.')
                addButton('record', 'voiceRecording()', 'Start Recording', "success") //, "bi bi-record-fill")
                document.getElementById("submit_button").disabled = true;
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
                document.getElementById("recordings").value = recordings

                if(allow_replay){
                    addAudio()
                    document.getElementById("alertMessage").innerHTML = "You can listen to your recording below to ensure a sufficient audio quality."
                    document.getElementById("reviewAlert").className = "alert alert-light text-dark shadow-sm"
                };
                addMessage('Submit or record again.')
                // addButton('download', 'downloadAudio()', 'Download Audio', "primary")
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



