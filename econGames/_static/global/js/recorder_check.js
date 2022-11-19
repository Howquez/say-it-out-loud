// Thank you Fran

console.log('recorder check is ready')

$(document).ready(function(){
  navigator.mediaDevices.getUserMedia({ audio: true})
  .then(function(stream) {
   audioContext = new AudioContext();
   analyser = audioContext.createAnalyser();
   microphone = audioContext.createMediaStreamSource(stream);
   javascriptNode = audioContext.createScriptProcessor(2048, 1, 1);


   analyser.smoothingTimeConstant = 0.8;
   analyser.fftSize = 1024;


   microphone.connect(analyser);
   analyser.connect(javascriptNode);
   javascriptNode.connect(audioContext.destination);

   javascriptNode.onaudioprocess = function() {
    var array = new Uint8Array(analyser.frequencyBinCount);
    analyser.getByteFrequencyData(array);
    var values = 0;
    var length = array.length;

    for (var i = 0; i < length; i++) {
     values += (array[i]);
   }

   var average = values / length;
   if (Math.round(average) <= 10) {
     $("#micUsed").val(false)
   }

 }
})
  .catch(function(err) {
 /* handle the error */
  });
})