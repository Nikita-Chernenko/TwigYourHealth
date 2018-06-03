var CALL_REQUEST_ACTION = 'call_request';
var CALL_END_ACTION = 'call_end';
var room;
var webrtc;
var $callRequestWrapper = $('#call-request-wrapper');
var $callVideoWrapper = $('#call-window-wrapper');
var withId;

function call(CALL_REQUEST, CALL_END) {
    chatSocket = new WebSocket(
        'ws://' + window.location.host + '/call/');
    chatSocket.onmessage = function (e) {
        var message = JSON.parse(e.data);
        console.log(message)
        console.log(message['action']);
        if (message['action'] === CALL_REQUEST_ACTION) {
            room = message['room'];
            withId = message['user_id'];
            $callRequestWrapper.show();
        }
        else if (message['action'] === CALL_END_ACTION) {
            webrtc.stopLocalVideo();
            webrtc.leaveRoom();
            webrtc.disconnect();

            $('#video-self').html('');
            $('#video-other').html('');

            $callVideoWrapper.hide();
        }
    };

    chatSocket.onclose = function () {
        console.error('Chat socket closed unexpectedly');
    };
    chatSocket.onopen = function () {
        console.log("Соединение установлено.");
    };

    chatSocket.onerror = function (error) {
        console.log("Ошибка " + error.message);
    };


    $('.call-request').click(function () {
        withId = parseInt($(this).parents('.chat-short').data('with-id'));
        console.log(withId);
        $.ajax({
            url: CALL_REQUEST.replace('0', withId),
            method: "POST",
            success: function (data) {
                webrtc = new SimpleWebRTC({
                    // the id/element dom element that will hold "our" video
                    localVideoEl: 'video-self',
                    // the id/element dom element that will hold remote videos
                    remoteVideosEl: 'video-other',
                    // immediately ask for camera access
                    autoRequestMedia: true,
                    signalingOptions: {"force new connection": true},

                });
                room = data['room'];
                console.log(room);
                $callVideoWrapper.show();
                console.log(room)
                webrtc.on('readyToCall', function () {
                    // you can name it anything
                    webrtc.createRoom(room, function (err, name) {
                        console.log(err);
                        console.log(name);
                    });
                });

                webrtc.on('videoAdded', function (video, peer) {
                    console.log('videoadded')
                    $('#video-other').html(video);
                });

            }
        });
        return false;
    });
    $('#accept-call-btn').click(function () {
        webrtc = new SimpleWebRTC({
            // the id/element dom element that will hold "our" video
            localVideoEl: 'video-self',
            // the id/element dom element that will hold remote videos
            remoteVideosEl: 'video-other',
            // immediately ask for camera access
            autoRequestMedia: true,
            signalingOptions: {"force new connection": true},
        });
        console.log(room);
        $callRequestWrapper.hide();
        $callVideoWrapper.show();
        webrtc.on('readyToCall', function () {
            webrtc.joinRoom(room);
        });
    });
    $('#end-call-btn').click(function () {
        console.log(room);
        console.log('test');
        $.ajax({
            url: CALL_END.replace('0', withId).replace('1', room),
            method: "POST",
            success: function () {

                webrtc.stopLocalVideo();
                webrtc.leaveRoom();
                webrtc.disconnect();
                $('#video-self').html('');
                $('#video-other').html('');
                $callVideoWrapper.hide();
            }
        })
    })
}