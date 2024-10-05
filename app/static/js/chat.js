$(document).ready(function () {

    var chat_channel = {};
    var message_draft = {};
    var chats = {};

    // Makes draft of messages which are not sent(, even stores after channel is changed.)
    $('#message_input').on("input", function () {
        var draft = $("#message_input").val().trim();
        if (draft != '') {
            message_draft[$("#chat").attr('chat_id')] = HTMLtoTEXT(draft);
        }
    })

    // Returns Usable DateTime String.
    function NowFormattedDateTime() {
        let date = new Date();
        let datePart = date.toISOString().split('T')[0];
        let timePart = date.toISOString().split('T')[1];
        let [time, millisecondsZ] = timePart.split('.');
        let milliseconds = millisecondsZ.slice(0, 6);
        let timezone = millisecondsZ.slice(6);
        return `${datePart} ${time}.${milliseconds}${timezone}`;
    };

    // In case if the message has html code, it makes them non-renderable.
    function HTMLtoTEXT(msg) {
        var div = document.createElement('div');
        div.appendChild(document.createTextNode(msg));
        return div.innerHTML;
    };


    function WSopen(e) {
        $("#ws-status").removeClass("bg-red-600");
        $("#ws-status").addClass("bg-green-600");

        $("#chat_form_disable").removeClass("flex").addClass("hidden");
        $("#chat_form").removeClass("hidden").addClass("flex");
    };

    function WSonmessage(e) {
        data = JSON.parse(e.data)
        if (data.type == "msg") {
            add_reveived_message(data.message, data.message_id, data.send_at)
            chats[data.chat_id].push({ 'chat_id': data.chat_id, 'message_id': data.message_id, 'message': data.message, 'send_at': data.send_at, 'send_to': chat_channel[data.chat_message] })
        } else {
            alert("data.type in not handled ")
        }
    };

    function WSclose(e) {
        $("#ws-status").removeClass("bg-green-600");
        $("#ws-status").addClass("bg-red-600");
        console.log("WS Dead");
        $("#chat_form").removeClass("flex").addClass("hidden");
        $("#chat_form_disable").removeClass("hidden").addClass("flex");
        setTimeout(WSConnect(), 5000);
    };

    function WSConnect() {
        console.log("trying to reconnect WS")
        ws = new WebSocket(window.location.origin + "/c/ws");
        ws.onopen = WSopen;
        ws.onmessage = WSonmessage;
        ws.onclose = WSclose;
    };


    // Shows or Hides the Green arrow send button on right of chat input.
    $("#chat_form").on("input", function () {
        if ($("#message_input").val().trim() == '') {
            $("#message_btn").hide()
        } else {
            $("#message_btn").show()
        }
    });

    // Calls 'sendMessage' func to send message through WS, Stores the message in dict 'chats', deletes the message draft, scrolls to the bottom.
    $("#chat_form").on("submit", function (e) {
        e.preventDefault();
        var input = $("#message_input").val().trim();
        if (input != '') {
            var current_time = NowFormattedDateTime()
            sendMessage(e, input, current_time);
            chats[$("#chat").attr('chat_id')].push({ 'chat_id': $("#chat").attr('chat_id'), 'message': input, 'send_at': current_time, 'send_to': $("#chat").attr('send_to') })
            $("#message_input").val('');
            $('#chat_box').scrollTop($('#chat_box')[0].scrollHeight);
            $("#message_btn").hide();
            delete message_draft[$("#chat").attr('chat_id')]
        }
    });

    // Sends message through WS, Adds the sent message to chat box.
    function sendMessage(e, input, current_time) {
        e.preventDefault();

        var payload = {
            'func': 'new_msg',
            'message': input,
            'chat_id': $("#chat").attr('chat_id'),
            'send_to': $("#chat").attr('send_to'),
            'send_at': current_time
        };
        ws.send(JSON.stringify(payload));
        add_sent_message(message = input, send_at = current_time)
    };

    // Fetches all users chat channels, calls 'add_chat_channel' func to add recipent profile on left panel.
    async function list_chats() {
        $.ajax({
            type: "get",
            url: window.location.origin + "/c/openChats",
            dataType: "json",
            success: function (response) {
                if (response.status) {
                    $("#chat_channel_loader").hide()
                    response.open_chat_list.forEach(channel => {
                        add_chat_channel(chat_id = channel.chat_id, send_to = channel.send_to)
                        chat_channel[channel.chat_id] = channel.send_to
                    });
                } else {
                    alert("Unable to fetch open chats: " + response.msg)
                }
            }
        });
    };

    // Adds chat channel to left panel.
    function add_chat_channel(chat_id, send_to) {
        $("#chat_channels").prepend(
            `<div id="${chat_id}" send_to="${send_to}" class="user p-1 my-2 bg-gray-900 rounded-lg text-white  h-min flex items-center">
            <img loading="lazy" src="https://picsum.photos/100" alt="profile_picture" class="rounded-lg h-10 w-10">
            <p class="ml-3 text-lg overflow-hidden">${send_to}</p>
        </div>`
        )

        document.getElementById(chat_id).addEventListener("click", function () {
            open_chat(chat_id);  // Call open_chat with chat_id
        });
    };

    // !!! Currently dont have message ID !!!
    function add_sent_message(message, send_at) {
        $("#chat_box_empty").hide()
        message = HTMLtoTEXT(message);
        $("#chat_box").append(
            `<div class="text-white">
                <div class="flex justify-end">
                    <div class="w-fit max-w-[70%] px-4 py-2 rounded-3xl bg-opacity-40 bg-gray-700">
                        <p>${message}</p>
                    </div>
                </div>
                <p class="text-xs text-right pr-4 pt-2">${send_at}</p>
            </div>`
        )
    };

    function add_reveived_message(message, message_id, send_at) {
        $("#chat_box_empty").hide()
        message = HTMLtoTEXT(message);
        $('#chat_box').append(
            `<div id="${message_id}" class="text-white">
                <div class="">
                    <div class="w-fit max-w-[70%] px-4 py-2 rounded-3xl bg-opacity-40 bg-gray-700">
                        <p>${message}</p>
                    </div>
                </div>
                <p class="text-xs  px-4 py-2">${send_at}</p>
            </div>`
        )
    };

    // Calls the server for chats for a chat-channel.
    async function get_chats_by_chat_id(chat_id) {
        try {
            const response = await fetch(window.location.origin + "/c/get_chat/" + chat_id);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json();
            if (data.status) {
                chats[chat_id] = data.chats;
                console.log("Chats fetched:", chats[chat_id]);
            } else {
                console.log("Unable to fetch chats: " + data.msg);
            }
        } catch (error) {
            console.error('There was a problem with the fetch operation:', error);
        }
    };

    // Open chat on frontend
    async function open_chat(chat_id) {
        if (chat_id != $("#chat").attr('chat_id')) {
            // show loader
            $("#support").show()
            $('#chat').hide()
            $("#idel-text").hide();
            $("#loader").show()

            if ($("#chat").attr('chat_id') != "") {
                $("#" + $("#chat").attr('chat_id')).removeClass("bg-orange-600").addClass("bg-gray-900");
            }
            $("#" + chat_id).removeClass("bg-gray-900").addClass("bg-orange-600");

            // setting current chat info
            $("#chat").attr('chat_id', chat_id).attr('send_to', chat_channel[chat_id]);
            $("#chat_user_pp").attr("src", "https://picsum.photos/100")
            $("#chat_user_id").text(chat_channel[chat_id]);


            // prepare chat box
            $("#chat_box").empty();
            if (!chats[chat_id]) {
                await get_chats_by_chat_id(chat_id);  // Wait for chats to be fetched
            }


            if (chats[chat_id].length != 0) {
                chats[chat_id].forEach(chat_message => {
                    if (chat_channel[chat_id] === chat_message.send_by) {
                        add_reveived_message(chat_message.message, chat_message.message_id, chat_message.send_at)
                    } else {
                        add_sent_message(chat_message.message, chat_message.send_at)
                    }
                });

                $('#chat_box').scrollTop($('#chat_box')[0].scrollHeight);
            } else {
                $("#chat_box").append(`<div id="chat_box_empty" class="min-h-full min-w-full flex justify-center items-center"><h3 class="text-white">No conservations yet, Send the first message.</h3></div>`)
            };

            $("#support").hide();

            $("#chat").show();

            // managing message Draft
            $("#message_input").val('');
            if (message_draft[chat_id]) {
                $("#message_input").val(message_draft[chat_id]);
            }
            $("#message_input").focus();


            $('#chat_box').scrollTop($('#chat_box')[0].scrollHeight);


            // hide loader
            $("#idel-text").show();
            $("#loader").hide();
        } else {
            $("#chat").hide();
            $("#chat_box").empty();
            $("#" + $("#chat").attr('chat_id')).removeClass("bg-orange-600").addClass("bg-gray-900");
            $("#chat").attr('chat_id', '').attr('send_to', '');

            $("#support").show();
        };
    };

    

    list_chats();
    WSConnect();


}); 