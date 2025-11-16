"""
Single demo: Assistant sends feedback as a separate message bubble
"""

import gradio as gr


def chat_function(message, history):
    """Simple chatbot that echoes the user's message"""
    return f"Here's my response to: {message}"


def feedback_handler(chatbot_history, liked_data: gr.LikeData):
    """
    When user clicks like/dislike, insert a separate feedback message
    right after the rated message.

    This creates two separate assistant bubbles in a row.
    """
    # Create the feedback message
    if liked_data.liked:
        feedback_msg = {
            "role": "assistant",
            "content": "Thank you for your positive feedback! 😊"
        }
    else:
        feedback_msg = {
            "role": "assistant",
            "content": "Sorry that wasn't helpful. I'll try to improve! 🙏"
        }

    insert_position = liked_data.index + 1

    updated_history = (
        chatbot_history[:insert_position] + [feedback_msg]
    )

    return updated_history


# Create the ChatInterface
demo = gr.ChatInterface(
    fn=chat_function,
    type="messages",
    flagging_mode="manual",
    flagging_options=["Like", "Dislike"],
    title="Feedback as Separate Message",
    description="Chat with the bot, then click 👍 or 👎 on any response. You'll see a separate feedback message appear right below it."
)

# Add the custom feedback handler
with demo:
    demo.chatbot.like(
        feedback_handler,
        inputs=[demo.chatbot],
        outputs=[demo.chatbot],
    )


if __name__ == "__main__":
    demo.launch()
