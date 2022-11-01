console.log("time recording ready!")

// Measure the time the calculator was opened
var startTime;
var endTime;
var increment = 0;
var sum = 0;

var myOffcanvas = document.getElementById('offcanvasGDPR')
myOffcanvas.addEventListener('show.bs.offcanvas',
function () {
    startTime = Date.now()
})

myOffcanvas.addEventListener('hidden.bs.offcanvas',
function () {
    endTime = Date.now();
    increment = endTime - startTime;
    sum += increment

    document.getElementById("privacy_time").value = sum/1000;
})