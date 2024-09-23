$( document ).ready(function() {

var ws = new WebSocket(window.location.origin+"/c/ws");

var send_to = 'ankit2'

ws.onmessage = function(event) {
    var messages = document.getElementById('messages');
    var message = document.createElement('li');
    message.appendChild(document.createTextNode(event.data));
    messages.appendChild(message);
};

function sendMessage(event) {
    event.preventDefault();
    var input = document.getElementById("message_input");
    var payload = {
        'func': 'new_msg', 
        'message': input.value, 
        'chat_id': 'abc',
        'send_to': send_to
    };
    ws.send(JSON.stringify(payload));

    input.value = '';
    event.preventDefault();
}

function list_chats(){
    $.ajax({
        type: "get",
        url: window.location.origin+"/c/openChats",
        dataType: "json",
        success: function (response) {
            if(response.status){
                response.open_chat_list.forEach(chanel => {
                    add_chat_channel(chat_id=chanel.chat_id, send_to=chanel.send_to)
                }); 
            }else{
                alert("Unable to fetch open chats: "+response.msg)
            }
        }
    });
}

function add_chat_channel(chat_id, send_to){
    $("#chat_channels").prepend(
    `<div id="user" chat_id="${chat_id}" send_to="${send_to}" class="p-1 my-2 bg-indigo-900 rounded-lg text-white  h-min flex items-center">
        <img loading="lazy" src="https://picsum.photos/100" alt="profile_picture" class="rounded-lg h-10">
        <p class="ml-3 text-lg overflow-hidden">${send_to}</p>
    </div>`
    )
}


function add_sent_message(message, chat_id, send_to){

}

function add_reveived_message(message, chat_id, send_to){

}

list_chats();


});