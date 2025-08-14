// Replace <Pi-IP> with your Raspberry Pi IP
const STREAM_URL = "http://192.168.2.2:8090/?action=stream";

document.addEventListener("DOMContentLoaded", function() {
    const stream = document.getElementById("videoStream");
    stream.src = STREAM_URL;

    let armed = false;

    window.toggleArm = function() {
        armed = !armed;
        document.getElementById("armBtn").innerText = armed ? "Disarm" : "Arm";
        fetch(`/api/arm?state=${armed}`);
    };

    window.refreshStream = function() {
        document.getElementById("videoStream").src = STREAM_URL + "&t=" + new Date().getTime();
    };

    window.takeSnapshot = function() {
        fetch('/api/snapshot')
        .then(resp => resp.blob())
        .then(blob => {
            let url = window.URL.createObjectURL(blob);
            let a = document.createElement('a');
            a.href = url;
            a.download = `snapshot_${Date.now()}.jpg`;
            a.click();
        });
    };

    window.viewLogs = function() {
        fetch('/api/logs')
        .then(resp => resp.text())
        .then(data => alert("Logs:\n\n" + data));
    };
});
