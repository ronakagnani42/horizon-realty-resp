function sendMessage() {
    const userInput = document.getElementById("userInput").value;
    const chatBox = document.getElementById("messages");

    chatBox.innerHTML += `<div><b>You:</b> ${userInput}</div>`;

    fetch(`/chatbot/get-response/?message=${encodeURIComponent(userInput)}`)
        .then(response => response.json())
        .then(data => {
            chatBox.innerHTML += `<div><b>Bot:</b> ${data.response}</div>`;
            document.getElementById("userInput").value = "";
        });
}
