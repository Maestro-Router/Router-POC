import time
import gradio as gr
from execute_backend import mock_llm
import random

# Global counters (in realistic units)
total_watt_hours = 0.0  # Watt-hours (Wh)
total_co2_grams = 0.0   # Grams of CO2

# Store feedback for each message
feedback_log = {}

def calculate_energy_impact(message, response):
    """
    Calculate realistic energy consumption and CO2 emissions for an LLM query.
    
    Typical LLM inference energy consumption:
    - Small queries: 0.002 - 0.005 Wh
    - Medium queries: 0.005 - 0.015 Wh
    - Large queries: 0.015 - 0.030 Wh
    
    CO2 emissions depend on energy grid (average ~475g CO2/kWh globally)
    """
    # Estimate tokens (rough approximation: 1 word ≈ 1.3 tokens)
    input_tokens = len(message.split()) * 1.3
    output_tokens = len(response.split()) * 1.3
    total_tokens = input_tokens + output_tokens
    
    # Energy consumption: approximately 0.001 Wh per 100 tokens (conservative estimate)
    # This is based on research showing GPT-3 uses about 1-5 Wh per 1000 tokens
    watt_hours = (total_tokens / 100) * 0.001
    watt_hours = max(0.002, min(watt_hours, 0.030))  # Clamp between 2-30 milliwatt-hours
    
    # CO2 emissions: average global grid intensity is ~475g CO2/kWh
    # Convert Wh to kWh and multiply by CO2 intensity
    co2_grams = (watt_hours / 1000) * 475
    
    return watt_hours, co2_grams

# Create the interface with additional components
with gr.Blocks(theme="ocean", css="""
    .file-compact { min-height: 50px !important; }
    .file-compact .wrap { min-height: 50px !important; }
""") as demo:
    gr.Markdown("# Maestro AI")
    gr.Markdown("*Environmental impact tracking for AI inference*")
    
    # Counter display at the top
    with gr.Row():
        watt_display = gr.Textbox(
            value="⚡ Energy: 0.000 Wh", 
            label="Total Energy Consumption", 
            interactive=False, 
            scale=1
        )
        co2_display = gr.Textbox(
            value="🌍 CO2: 0.000 g", 
            label="Total CO2 Emissions", 
            interactive=False, 
            scale=1
        )
    
    # Chat interface
    chatbot = gr.Chatbot(type="messages", height=400)
    
    # Feedback display
    feedback_display = gr.Textbox(
        label="Feedback Log",
        value="",
        interactive=False,
        visible=False,
        max_lines=3
    )
    
    # Message input with file upload button on the side
    with gr.Row():
        msg = gr.Textbox(
            label="Your message", 
            placeholder="Type your message here...",
            show_label=False,
            container=False,
            scale=10
        )
        file_upload = gr.UploadButton(
            "📎",
            file_count="multiple",
            file_types=[".txt", ".pdf", ".doc", ".docx", ".csv", ".json", ".py", ".md"],
            scale=0,
            size="lg"
        )
    
    # Buttons below the text input
    with gr.Row():
        submit = gr.Button("Send", variant="primary", scale=1)
        clear = gr.Button("Clear", scale=1)
    
    gr.Examples(
        examples=["Je veux savoir plus sur l'intelligence artificielle", "Bonjour, comment ça va?", "Explique-moi la photosynthèse"],
        inputs=msg
    )
    
    # Info section
    gr.Markdown("""
    ### ℹ️ About these metrics
    - **Energy**: Measured in Watt-hours (Wh). Average query uses 0.002-0.030 Wh
    - **CO2**: Measured in grams. Based on average global grid intensity (~475g CO2/kWh)
    - For context: A typical smartphone charge uses about 5-10 Wh
    """)
    
    def respond(message, chat_history, files):
        global total_watt_hours, total_co2_grams
        
        if not message.strip():
            return "", chat_history, f"⚡ Energy: {total_watt_hours:.3f} Wh", f"🌍 CO2: {total_co2_grams:.3f} g", None, gr.update(visible=False), ""
        
        # Build the full message with file information
        full_message = message
        user_display_message = message
        
        # Only process files if they exist
        if files:
            file_info = "\n\n📎 Attached files:\n"
            for file in files:
                if hasattr(file, 'name'):
                    file_path = file.name if hasattr(file, 'name') else str(file)
                    file_info += f"- {file_path}\n"
                    print(f"📎 Attachment location: {file_path}")
                else:
                    file_info += f"- {str(file)}\n"
                    print(f"📎 Attachment location: {str(file)}")
            full_message += file_info
            user_display_message += file_info
        
        # Get response
        response = mock_llm(full_message)
        bot_message = response["response"]
        
        # Calculate realistic energy impact
        watt_hours, co2_grams = calculate_energy_impact(full_message, bot_message)
        
        # Increment counters
        total_watt_hours += watt_hours
        total_co2_grams += co2_grams
        
        # Update chat history
        chat_history.append({"role": "user", "content": user_display_message})
        chat_history.append({"role": "assistant", "content": bot_message})
        
        # Update counters display with realistic units
        watt_text = f"⚡ Energy: {total_watt_hours:.3f} Wh"
        co2_text = f"🌍 CO2: {total_co2_grams:.3f} g"
        
        # Clear the message input, update chat, update counters, and clear files
        return "", chat_history, watt_text, co2_text, None, gr.update(visible=False), ""
    
    def handle_like_event(data: gr.LikeData):
        """Handle like/dislike - show feedback in a display"""
        global feedback_log
        
        message_id = data.index
        feedback_type = "👍 Liked" if data.liked else "👎 Disliked"
        
        # Store feedback
        feedback_log[message_id] = feedback_type
        
        # Print to console with more detail
        print(f"\n{'='*50}")
        print(f"{feedback_type} message at index: {message_id}")
        print(f"Message content: {data.value}")
        print(f"{'='*50}\n")
        
        # Create feedback summary
        feedback_text = f"{feedback_type} message #{message_id}"
        
        return gr.update(visible=True, value=feedback_text)
    
    def reset_counters():
        global total_watt_hours, total_co2_grams, feedback_log
        total_watt_hours = 0.0
        total_co2_grams = 0.0
        feedback_log = {}
        return [], "⚡ Energy: 0.000 Wh", "🌍 CO2: 0.000 g", None, gr.update(visible=False), ""
    
    # Event handlers
    submit.click(
        respond,
        inputs=[msg, chatbot, file_upload],
        outputs=[msg, chatbot, watt_display, co2_display, file_upload, feedback_display, feedback_display]
    )
    
    msg.submit(
        respond,
        inputs=[msg, chatbot, file_upload],
        outputs=[msg, chatbot, watt_display, co2_display, file_upload, feedback_display, feedback_display]
    )
    
    clear.click(
        reset_counters, 
        outputs=[chatbot, watt_display, co2_display, file_upload, feedback_display, feedback_display]
    )
    
    # Like/Dislike handler - show feedback in display
    chatbot.like(
        handle_like_event,
        inputs=None,
        outputs=[feedback_display]
    )

if __name__ == "__main__":
    demo.launch()
