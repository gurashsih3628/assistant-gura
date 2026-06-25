(() => {
    // 1. DOM Elements
    const input = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-box");
    const sendBtn = document.getElementById("send-btn");

    // Safety check: Ensure UI elements exist before running code
    if (!input || !chatBox || !sendBtn) {
        console.error("Gura Assistant Error: Core UI elements missing from the DOM.");
        return;
    }

    // 2. Helper Functions
    const appendMessage = (sender, text, id = "") => {
        const idAttribute = id ? `id="${id}"` : "";
        
        // Using clean template literals with backticks
        chatBox.innerHTML += `
            <div class="${sender}" ${idAttribute}>
                ${text}
            </div>
        `;
        // Auto-scroll to the latest message
        chatBox.scrollTop = chatBox.scrollHeight;
    };

    // 3. Core Chat Logic
    async function sendMessage() {
        const message = input.value.trim();
        if (!message) return;

        // Display user message and clear input
        appendMessage("user", message);
        input.value = "";

        // Display typing indicator
        const typingId = `typing-${Date.now()}`;
        appendMessage("bot", "Gura is typing...", typingId);

        try {
            const response = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message, session_id: "default" })
            });

            if (!response.ok) throw new Error("Network response was not ok");

            const data = await response.json();
            
            // Remove typing indicator
            document.getElementById(typingId)?.remove();

            // Format line breaks and display response
            const botReply = String(data.reply || data.error || "No response").replace(/\n/g, "<br>");
            appendMessage("bot", botReply);

        } catch (error) {
            console.error("Chat Error:", error);
            document.getElementById(typingId)?.remove();
            appendMessage("bot", "❌ Connection failed. Please try again.");
        }
    }

    // 4. Event Listeners
    sendBtn.addEventListener("click", sendMessage);

    input.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            event.preventDefault();
            sendMessage();
        }
    });
})();