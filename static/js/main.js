$(document).ready(function() {
    // Function to add a message to the chat
    function addMessage(message, isUser = false) {
        const messageClass = isUser ? 'user-message' : 'bot-message';
        const messageHTML = `
            <div class="message ${messageClass}">
                <div class="message-content">
                    ${formatMessage(message)}
                </div>
            </div>
        `;
        $('#messages').append(messageHTML);
        
        // Scroll to the bottom
        scrollToBottom();
    }
    
    // Function to format the message with proper line breaks
    function formatMessage(message) {
        // Replace newlines with paragraph tags
        if (message.includes('\n')) {
            return message.split('\n').map(line => {
                return line.trim() ? `<p>${line}</p>` : '';
            }).join('');
        }
        return `<p>${message}</p>`;
    }
    
    // Function to scroll the messages container to the bottom
    function scrollToBottom() {
        const messagesContainer = document.getElementById('messages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    // Function to show typing indicator
    function showTypingIndicator() {
        const typingHTML = `
            <div class="message bot-message" id="typing-indicator">
                <div class="message-content">
                    <p><em>Typing...</em></p>
                </div>
            </div>
        `;
        $('#messages').append(typingHTML);
        scrollToBottom();
    }
    
    // Function to remove typing indicator
    function removeTypingIndicator() {
        $('#typing-indicator').remove();
    }
    
    // Function to send user message to the server and get response
    function sendMessage(message) {
        // Show user message
        addMessage(message, true);
        
        // Show typing indicator
        showTypingIndicator();
        
        // Send to server
        $.ajax({
            url: '/get_response',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ message: message }),
            success: function(data) {
                // Remove typing indicator
                removeTypingIndicator();
                
                // Show bot response
                addMessage(data.response);
            },
            error: function() {
                // Remove typing indicator
                removeTypingIndicator();
                
                // Show error message
                addMessage("Sorry, I encountered an error. Please try again later.");
            }
        });
    }
    
    // Event handler for form submission
    $('#chat-form').submit(function(e) {
        e.preventDefault();
        const userInput = $('#user-input').val().trim();
        
        if (userInput) {
            // Clear input field
            $('#user-input').val('');
            
            // Send message
            sendMessage(userInput);
        }
    });
    
    // Event handler for suggestion buttons
    $('.suggestion-btn').click(function() {
        const query = $(this).data('query');
        sendMessage(query);
    });
    
    // Focus input field on page load
    $('#user-input').focus();
    
    // Initial scroll to bottom
    scrollToBottom();
}); 