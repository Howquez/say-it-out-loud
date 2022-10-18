console.log("liveRecv ready")

function liveRecv(data) {
    console.log("received message:", data);
    document.getElementById("test-message").innerHTML = "<small>FYI: The base64 string contains <b>"+data+"</b> characters.</small>";
}