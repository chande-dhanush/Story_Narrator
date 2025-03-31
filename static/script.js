let currentStep = 0;
let chatData = {
    user: "",
    genre: "",
    tone: "",
    characters: "",
    skills: "",
    related: ""
};

document.addEventListener('DOMContentLoaded', function() {
    const chatbox = document.getElementById('chatbox').querySelector('.messages');
    
    // Display the welcome message and then the first question
    appendBotMessage("Welcome to Dream Scraper!");
    setTimeout(() => {
        appendBotMessage("What character name do you want to use?");
        appendBotMessage("Also mention the skills that you want to have");
        currentStep++;
    }, 1000);

    // Send button click event
    document.getElementById('sendButton').addEventListener('click', sendMessage);
    
    // User input handling with Enter key
    document.getElementById('userInput').addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });
});

// Function to send a message
function sendMessage() {
    const userInput = document.getElementById('userInput');
    const userMessage = userInput.value;

    if (userMessage.trim() === "") return; // Prevent empty messages

    appendUserMessage(userMessage);
    userInput.value = ""; // Clear input field

    handleUserMessage(userMessage);
}

// Function to append user's message
function appendUserMessage(message) {
    const chatbox = document.getElementById('chatbox').querySelector('.messages');
    const messageElement = document.createElement('div');
    messageElement.classList.add('user-message');
    messageElement.innerHTML = `<div class="message-content">${message}</div>`;
    chatbox.appendChild(messageElement);
    chatbox.scrollTop = chatbox.scrollHeight; // Scroll to bottom
    scrollToBottom();
}

// Function to append bot's message
function appendBotMessage(message) {
    const chatbox = document.getElementById('chatbox').querySelector('.messages');
    const messageElement = document.createElement('div');
    messageElement.classList.add('bot-message');
    messageElement.innerHTML = `<div class="message-content">${message}</div>`;
    chatbox.appendChild(messageElement);
    chatbox.scrollTop = chatbox.scrollHeight; // Scroll to bottom
    scrollToBottom();
}

// Function to append image
function appendImage(imgSrc) {
    const chatbox = document.getElementById('chatbox').querySelector('.messages');
    const imageMessage = `<img class="generated-image" src="${imgSrc}" alt="Generated Image">`;
    chatbox.innerHTML += imageMessage;
    chatbox.scrollTop = chatbox.scrollHeight;
    scrollToBottom();
}

// Function to append audio
function appendAudio(audioSrc) {
    const chatbox = document.getElementById('chatbox').querySelector('.messages');
    const audioMessage = `<audio controls><source src="${audioSrc}" type="audio/mp3"></audio>`;
    chatbox.innerHTML += audioMessage;
    chatbox.scrollTop = chatbox.scrollHeight;
    scrollToBottom();
}

// Function to handle user message and update chatbot data
function handleUserMessage(message) {
    if (message.toLowerCase() === "exit") {
        appendBotMessage("Okay, let's stop here. Hope you enjoyed!");
        appendBotMessage("If you want to start again, just give your character name and your skills.");
        currentStep = 0; // Reset the step to start a new conversation
        chatData = {
            user: "",
            genre: "",
            tone: "",
            characters: "",
            skills: "",
            related: ""
        }; // Reset chat data
        return;
    }

    switch (currentStep) {
        case 1:
            chatData.user = message;
            appendBotMessage("Awesome! What genre do you prefer?");
            break;
        case 2:
            chatData.genre = message;
            appendBotMessage("Great choice! What tone do you want for the story?");
            break;
        case 3:
            chatData.tone = message;
            appendBotMessage("Got it! What characters do you want in your story?");
            break;
        case 4:
            chatData.characters = message;
            appendBotMessage("Awesome! What skills should the characters have?");
            break;
        case 5:
            chatData.skills = message;
            appendBotMessage("Perfect! Any related works or themes you’d like to include?");
            break;
        case 6:
            chatData.related = message;
            appendBotMessage("Generating your story... \napprox time:25s");
            // Call the function to generate the story based on chatData here
            generateStory();
            break;
        default:
            appendBotMessage("I don't understand that. Please provide the necessary details.");
            break;
    }

    // Increment the current step after processing the user's input
    if (currentStep < 6) {
        currentStep++;
    }
}

// Function to generate the story based on chat data (placeholder function)
function generateStory() {
    fetch('/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(chatData)
    })
    .then(response => response.json())
    .then(data => {
        appendBotMessage(data.story);
        appendImage(data.image_path);
        appendAudio(data.audio_path);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
function scrollToBottom() {
    const chatbox = document.querySelector('.chatbox');
    chatbox.scrollTop = chatbox.scrollHeight;
}

