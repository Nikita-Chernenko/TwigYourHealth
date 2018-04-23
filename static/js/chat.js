function chat(MESSAGE_CREATE, USER_RETRIEVE, MESSAGE_LIST, IS_PATIENT, IS_DOCTOR) {
    var chatSocket;
    $('.send-sms').on('click', function () {
        console.log(chatSocket);
        chatSocket.send(JSON.stringify({'text': 'test'}))
    });
    $('#open-chat').on('click', function () {
        $(this).parents('.chat-block').hide();
        $('#chat-block-short').show();

    });
    $('.chat-close').on('click', function () {
        $(this).parents('.chat-block').hide();
        $('#chat-icon').show();
    });
    $('.chat-short').on('click', function () {
        var el = $(this);
        el.parents('.chat-block').hide();
        var chat = $('#chat-block-full');
        chat.show();
        var chat_id = el.data('chat-id');
        chat.data('chat-id', chat_id);
        var user_id = parseInt(el.data('user-id'));
        var with_id = parseInt(el.data('with-id'));
        var message_block = chat.find('.chat-messages');
        chatSocket = new WebSocket(
            'ws://' + window.location.host +
            '/chat/' + with_id + '/');
        chatSocket.onmessage = function (e) {
            var message = JSON.parse(e.data);
            console.log(message);
            var message_template = $($('#invisible-text-message-block').html());
            console.log(message['user_id'], user_id);
            if (message['user_id'] === user_id) {
                message_template.addClass('other')
            }
            else {
                message_template.addClass('self')
            }
            if (IS_PATIENT && message['patient_read'] || IS_DOCTOR && message['doctor_read']) {
                message_template.addClass('read')
            }
            else {
                message_template.addClass('unread');
            }
            message_template.find('.message-text').html(message['text']);
            message_template.find('.message-time').html(message['timestamp']);
            message_block.append(message_template);
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
        $.ajax({
            method: "get",
            url: USER_RETRIEVE.replace("0", user_id),
            success: function (response) {
                var data = JSON.parse(response)[0]['fields'];
                chat.find('.interlocutor-name').html(data.username);
            }
        });
        $('.interlocutor-avatar').html($(this).find('.chat-avatar').clone());
        chat.find('.chat-messages').html('');
        $.ajax({
            method: "get",
            url: MESSAGE_LIST.replace("0", chat_id),
            success: function (response) {
                var messages = JSON.parse(response);
                $('#chat-block-full').find('.chat-messages').html('');
                for (var i = 0; i < messages.length; i++) {
                    var message_template = $($('#invisible-text-message-block').html());
                    var message = messages[i]['fields'];
                    var message_id = messages[i]['pk'];
                    message_template.data('message-id', message_id);

                    if (message['author'] + '' === user_id + '') {
                        message_template.addClass('other')
                    }
                    else {
                        message_template.addClass('self')
                    }
                    if (IS_PATIENT && message['patient_read'] || IS_DOCTOR && message['doctor_read']) {
                        message_template.addClass('read')
                    }
                    else {
                        message_template.addClass('unread');
                    }
                    message_template.find('.message-text').html(message['text']);
                    message_template.find('.message-time').html(message['timestamp']);
                    message_block.append(message_template);
                }
            }
        })
    });
    $('.chat-back').on('click', function () {
        $(this).parents('.chat-block').hide();
        $('#chat-block-short').show()
    });
    $('#send-message').on('click', function () {
        var text = $('#message-input').val();
        var chat_id = $('#chat-block-full').data('chat-id');
        if (text.length > 0) {
            $.ajax({
                method: "post",
                data: {'text': text, 'chat': chat_id},
                url: MESSAGE_CREATE,
                success: function (response) {
                    console.log(response);
                }


            })
        }
    });
}