let i = document.getElementById("id_sliderDecision"),
    o = document.querySelector('output');
var suffix = " cents";

o.innerHTML = " ";

// use 'change' instead to see the difference in response
i.addEventListener('input', function () {
    if(i.value==1){
        suffix = " cent"
    } else {
        suffix = " cents"
    }
    o.innerHTML = "<small>I allocate " + i.value + suffix + ".</small>";
}, false);


function showValue(newValue) {
    i.innerHTML = newValue;
}

$('#slider').change(function(e) {
    showValue($(this).val());

});