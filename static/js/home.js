$(document).ready(function() {
    $("#btnFace").click(function(){
        document.location.href = "http://localhost:5555/face";
    });

    $("#btnFinger").click(function(){
        document.location.href = "http://localhost:5555/fingerprint";
    });
});