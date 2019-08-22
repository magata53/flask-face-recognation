// link to fingerprint or home
   if($('input:hidden').val() === 'face') {
    setTimeout(function() {
        document.location.href = "http://localhost:5555/fingerprint"
    }, 3000)
   } else {
    setTimeout(function() {
        document.location.href = "http://localhost:5555/"
    }, 3000)
   }