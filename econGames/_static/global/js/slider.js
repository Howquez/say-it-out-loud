console.log("Slider Ready")


// disable submit button (to later enable it after the slider was used.
document.getElementById("submit_button").disabled = true;

// define slider as i and output text as o
let i = document.getElementById("id_sliderDecision"),
    o = document.querySelector('output');

// create a suffix for the value displayed in o
var suffix;

// create a default text displayed in o when opening the page
o.innerHTML = "<small class='text-dark'>Click on the slider to enter your decision.</small>";

// use 'change' instead to see the difference in response
i.addEventListener('input', function () {

    // change class attribute and thus, style defined in the corresponding css file
    i.classList.remove('notclicked');

    // enable submit button
    document.getElementById("submit_button").disabled = false;

    // fill suffix
    if(i.value==1){
        suffix = " cent"
    } else {
        suffix = " cents"
    }

    // write output text in o
    o.innerHTML = "<small>I allocate " + i.value + suffix + ".</small>";

}, false);
