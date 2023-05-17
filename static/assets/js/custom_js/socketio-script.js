 var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port, {
    transports: ['websocket']
});

 socket.on('handle_data', function(data) {
    console.log(data)
    name = data['fullname_var']
    socket.emit('join', {'name': name});
});

 socket.on('join', function(data) {
    message.textContent = data['message'];
    document.querySelector('#join').append(message);
});

 socket.on('message', function(data) {
    var message = document.createElement('li');
    message.textContent = data['sender'] + ': ' + data['message'];
    document.querySelector('#messages').append(message);
});

 function sendMessage() {
    var message = document.querySelector('#message').value;
    socket.emit('message', {'message': message});
    document.querySelector('#message').value = '';
}