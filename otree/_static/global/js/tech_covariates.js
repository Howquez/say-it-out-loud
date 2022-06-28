console.log("tracking ready!")

// Device Type Info
// credit: https://stackoverflow.com/a/65463713
function getResolution() {
  document.getElementById('width').value  = window.screen.width;
  document.getElementById('height').value = window.screen.height;
  document.getElementById('devicePixelRatio').value = window.devicePixelRatio;
  // console.log(`Your screen resolution is: ${realWidth} x ${realHeight}`);
}

/* note that browser (user agent) sniffing appears to be error prone and bad practice
  https://stackoverflow.com/a/3540295
  or
  https://developer.mozilla.org/en-US/docs/Learn/Tools_and_testing/Cross_browser_testing/JavaScript#using_bad_browser_sniffing_code


function isMobile() {
    const toMatch = [
        /Android/i,
        /iPhone/i,
        /iPad/i,
    ];
    return toMatch.some((item) => navigator.userAgent.match(item));
}

document.getElementById('is_mobile').value = isMobile() ? 1 : 0;
*/


// Geo Location
function getLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(showPosition, showError);
  } else {
    document.getElementById('latitude').value  = "Geolocation is not supported by this browser.";
    document.getElementById('longitude').value = "Geolocation is not supported by this browser.";
  }
}

function showPosition(position) {
  document.getElementById('latitude').value = position.coords.latitude
  document.getElementById('longitude').value = position.coords.longitude;
}

function showError(error) {
  switch(error.code) {
    case error.PERMISSION_DENIED:
      document.getElementById('latitude').value  = "User denied the request for Geolocation."
      document.getElementById('longitude').value = "User denied the request for Geolocation."
      break;
    case error.POSITION_UNAVAILABLE:
      document.getElementById('latitude').value  = "Location information is unavailable."
      document.getElementById('longitude').value = "Location information is unavailable."
      break;
    case error.TIMEOUT:
      document.getElementById('latitude').value  = "The request to get user location timed out."
      document.getElementById('longitude').value = "The request to get user location timed out."
      break;
    case error.UNKNOWN_ERROR:
      document.getElementById('latitude').value  = "An unknown error occurred."
      document.getElementById('longitude').value = "An unknown error occurred."
      break;
  }
}

// Call functions
getResolution();
getLocation();