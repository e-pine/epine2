const id = JSON.parse(document.getElementById('json-username').textContent);
const message_username = JSON.parse(document.getElementById('json-message-username').textContent);
const receiver = JSON.parse(document.getElementById('json-username-receiver').textContent);
const socket = new WebSocket(
    'ws://' + window.location.host + '/ws/' + id + '/'
);

socket.onopen = function (e) {
    console.log("CONNECTION ESTABLISHED");
}

socket.onclose = function (e) {
    console.log("CONNECTION LOST");
}

socket.onerror = function (e) {
    console.log(e);
}

socket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    console.log('Received data:', data);
    const chatBody = document.querySelector('#chat-body');

    const messageContainer = document.createElement('div');
    messageContainer.classList.add('message-container');
    messageContainer.classList.add('d-flex');

    if (data.username === message_username) {
        messageContainer.classList.add('justify-content-end');
    } else {
        messageContainer.classList.add('justify-content-start');
    }

    const messageElement = document.createElement('div');
    messageElement.classList.add('message');
    messageElement.classList.add(`bg-${data.username === message_username ? 'success' : 'primary'}`);
    messageElement.classList.add('p-2', 'mt-2', 'mr-5', 'shadow-sm', 'text-white', 'rounded');

    function linkify(text) {
        return text.replace(/(https?:\/\/[^\s]+)/g, function (url) {
            // Add a space before the URL if it's at the beginning of the message
            const linkElement = document.createElement('a');
            linkElement.href = url;
            linkElement.target = '_blank';
            linkElement.style.color = 'white'; // Set the text color to white
            linkElement.textContent = url;
    
            return (text.indexOf(url) === 0) ? ` ${linkElement.outerHTML}` : linkElement.outerHTML;
        });
    }
    

    const messageContent = document.createElement('div');
    messageContent.innerHTML = linkify(data.message);

    // Append both regular messages and messages with links
    messageElement.appendChild(messageContent);

    // Append the timestamp
    messageElement.innerHTML += `<br>${'just now'}`;

    messageContainer.appendChild(messageElement);
    chatBody.appendChild(messageContainer);
    chatBody.scrollTop = chatBody.scrollHeight; // Scroll to the bottom of the chat
}

document.querySelector('#chat-message-submit').onclick = function (e) {
    const messageInput = document.querySelector('#message_input');
    const message = messageInput.value.trim();

    if (message !== '') {
        // Check if the message is a link
        const isLink = message.startsWith('http');

        // Modify this part to ensure the "link" attribute is set correctly
        const data = {
            'message': message,
            'username': message_username,
            'receiver': receiver,
        };

        if (isLink) {
            data.link = message;
        }

        socket.send(JSON.stringify(data));

        messageInput.value = '';
    }
}
