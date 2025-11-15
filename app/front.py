import time
import gradio as gr

from execute_backend import mock_llm

def send(message, history):
    # will call send function from back
    response = mock_llm(message)
    #return f"Vous avez envoyé: {message} which should return: {response}" 
    return response["response"]

def echo_multimodal(message, history):
    response = []
    response.append("You wrote: '" + message["text"] + "' and uploaded:")
    if message.get("files"):
        for file in message["files"]:
            response.append(gr.File(value=file))
    return response

def echo_history(message, history):
    return f"Vous avez message {message} + \n historique: {history}" 

demo = gr.ChatInterface(
    fn=send,
    title="Maestro AI",
    type="messages",
    flagging_mode="manual",
    flagging_options=["Like", "Spam", "Inappropriate", "Other"],    
    cache_mode="eager",
    examples=["Je veux savoir plus sur ", "Bonjour, ", ""],
    run_examples_on_click=False,
    save_history=True,
    delete_cache=None,
    multimodal=True,
    theme="ocean"
)

demo.saved_conversations.secret = "abcdefasd6200683922"
demo.saved_conversations.storage_key = "_saved_conversations"

if __name__ == "__main__":
    demo.launch()
