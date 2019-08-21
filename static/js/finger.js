 // initial socket io
 var socket = io.connect('http://localhost:5000');

      // get data face
      socket.on('connect', function() {

        // join room face
        socket.emit( 'join_room', 'room_fingerprint' );
        socket.emit( 'join_room', 'room_access_denied' );

        socket.on('fingerprint_data', function(data) {
            var json = JSON.parse(data);

            if(json) {

                $.ajax({
                    url: 'http://localhost:5555/api/post/fingerprint',
                    type: 'post',
                    dataType: 'json',
                    contentType: 'application/json',
                    success: function (data) {
                        console.log(data)
                        socket.emit('leave_room', 'room_fingerprint')
                        socket.emit('leave_room', 'room_access_denied')
                        setTimeout(function() {
                            document.location.href = "http://localhost:5555/fingerprint-success"
                        }, 3000)
                    },
                    data: JSON.stringify(json)
                });
            }
        });

        socket.on('access_denied_data', function(data) {
            var json = JSON.parse(data);

            if(json) {

                $.ajax({
                    url: 'http://localhost:5555/api/post/access-denied',
                    type: 'post',
                    dataType: 'json',
                    contentType: 'application/json',
                    success: function (data) {
                        console.log(data)
                        socket.emit('leave_room', 'room_fingerprint')
                        socket.emit('leave_room', 'room_access_denied')
                        setTimeout(function() {
                            document.location.href = "http://localhost:5555/access_denied"
                        }, 3000)
                    },
                    data: JSON.stringify(json)
                });
            }
        });
      });