$(document).ready(function () {
    var toggleButton = $("#toggleFullScreen");
    var chatCard = $("#chatCard");

    toggleButton.click(function () {
        chatCard.toggleClass("fullscreen");
        toggleFullscreenButtons();
        adjustChatMessagesSize();
    });

    $("#exitFullScreen").click(function () {
        chatCard.removeClass("fullscreen");
        toggleFullscreenButtons();
        adjustChatMessagesSize();
    });

    function toggleFullscreenButtons() {
        var isFullScreen = chatCard.hasClass("fullscreen");
        var expandIcon = '<i class="fas fa-expand-arrows-alt"></i>';
        var compressIcon = '<i class="fas fa-compress-arrows-alt"></i>';

        toggleButton.html(isFullScreen ? compressIcon : expandIcon);
    }

    function adjustChatMessagesSize() {
        var isFullScreen = chatCard.hasClass("fullscreen");
        var chatMessages = $("#chat-body");

        if (isFullScreen) {
            chatMessages.css("max-width", "2000px");
        } else {
            chatMessages.css("max-width", "400px");
        }
    }
});



// $(document).ready(function () {
//     var toggleButton = $("#toggleFullScreen");
//     var cardBody = $(".card-body.fullscreenable");

//     toggleButton.click(function () {
//         cardBody.toggleClass("fullscreen");
//     });
// });

// .fullscreenable.fullscreen {
//     position: fixed;
//     top: 0;
//     left: 0;
//     width: 100%;
//     height: 100%;
//     z-index: 1000;
    
/* <div class="card card-success p-1 mx-auto" id="chatCard" style="max-width: 600px;">
    <div class="card-header">
        <a href="{% url 'bidding_rooms_low' %}" class="back-link"><i class="fas fa-arrow-left" style="color: #000;"></i></a>
        <div class="card-tools">
            <button type="button" class="btn" id="toggleFullScreen"><i class="fas fa-expand-arrows-alt"></i></button>
        </div>
    </div>
    <div class="card-body fullscreenable" style="max-height: 600px; overflow-y: auto;">
        <div class="chat-messages space-y-3" id="chat-messages">
            {% for message in messages %}
            <div class="message-container {% if message.user.username == request.user.username %}sender{% else %}receiver{% endif %}">
                {% if message.user != request.user %} 
                <p class="font-weight-bold">{{ message.user.username }}</p>
                {% else %}
                <i class='far fa-user'></i>
                {% endif %}
                &nbsp;&nbsp;
                <div class="message-content rounded p-3 mb-3">
                    <p>{{ message.content }}</p>
                    <p class="message-time">{{ message.date_added|hours_ago }}</p>
                </div>
            </div>
            {% endfor %}
            <style>
                .message-container.default-message {
                    justify-content: center;
                    align-items: center;
                }
            </style>
        </div>
        <div class="card-footer">
            <form action="." method="post" class="d-flex">
                {% csrf_token %}
                <input type="text" name="content" class="form-control flex-grow-1 mr-2" id="chat-message-input" style="background-color: rgb(219, 206, 206);">
                <button type="submit" class="btn btn-primary px-4" id="chat-message-submit">Send</button>
            </form>
        </div>
    </div>
    <!-- /.card-body -->
</div> */