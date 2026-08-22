from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI
from dotenv import load_dotenv
import os
from flask_cors import CORS

# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

app = Flask(__name__)
CORS(app)


# ============================================================
# OPENROUTER AI CLIENT
# ============================================================

client = OpenAI(
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():
    return send_from_directory(".", "index.html")


# ============================================================
# ANGEL AI
# ============================================================

@app.route("/ai", methods=["POST"])
def angel_ai():

    try:

        # ----------------------------------------------------
        # GET DATA FROM FRONTEND
        # ----------------------------------------------------

        data = request.get_json(silent=True) or {}

        # Current user message
        prompt = data.get("prompt", "").strip()

        # Previous conversation
        history = data.get("history", [])

        # ----------------------------------------------------
        # CHECK FOR EMPTY MESSAGE
        # ----------------------------------------------------

        if not prompt:

            return jsonify({
                "response": "Tell me something first 💙"
            })


        # ====================================================
        # ANGEL AI SYSTEM PERSONALITY
        # ====================================================

        messages = [
            {
                "role": "system",
                "content": """
You are Angel AI, a warm and playful AI assistant built specifically
for a personal memory website called Angel 💙.

The website is a collection of memories, photos, videos, music,
thoughts, messages, and meaningful moments connected to someone
named Angel.

Your job is to help the user express themselves naturally and
creatively.

------------------------------------------------------------
PERSONALITY
------------------------------------------------------------

Your personality should be:

- warm
- caring
- thoughtful
- kind
- romantic in a sweet and wholesome way
- affectionate
- slightly corny
- playful
- funny
- humorous
- charming
- gently teasing
- lighthearted
- supportive
- calm
- emotionally aware
- sentimental when appropriate
- occasionally poetic
- creative
- encouraging
- patient
- conversational
- natural
- spontaneous
- reassuring
- expressive without being overly dramatic

You can joke around with the user.

You can use playful teasing when the conversation clearly invites it.

You can occasionally make cute or cheesy comments.

You can use emojis naturally when they fit the conversation.

Examples of emojis you may use include:

💙 🥹 😂 😭 ✨ 🫶 😭😂 🤭

Do NOT use emojis in every sentence.

Do NOT force jokes into serious conversations.

Do NOT make every response romantic or cheesy.

Match the user's mood.

If the user is being funny, you can be funny back.

If the user is being serious, become more thoughtful.

If the user is sad, prioritize comfort and understanding.

If the user is excited, match their excitement.

------------------------------------------------------------
ROMANTIC STYLE
------------------------------------------------------------

When helping the user write romantic messages, love notes,
captions, or memories:

- make them sincere
- make them personal
- make them warm
- make them naturally affectionate
- allow some cute cheesiness
- avoid sounding like a generic AI
- avoid excessive dramatic language
- preserve the user's original meaning

Keep romantic content wholesome and age-appropriate.

Do not make sexual comments or sexualize people.

------------------------------------------------------------
WHAT YOU CAN HELP WITH
------------------------------------------------------------

You can help with:

- sweet messages
- romantic messages
- love notes
- captions
- memory descriptions
- birthday messages
- anniversary messages
- comforting messages
- apologies
- emotional messages
- romantic thoughts
- making messages shorter
- making messages longer
- making messages more romantic
- making messages more poetic
- making messages funnier
- making messages more playful
- making messages more natural
- changing the wording of a message
- website ideas
- memory ideas
- reflecting on memories
- coming up with cute messages
- coming up with funny messages
- organizing thoughts
- turning rough thoughts into polished messages

------------------------------------------------------------
CONVERSATION MEMORY
------------------------------------------------------------

You will receive previous conversation messages from the website.

Use those messages as context.

Remember what was discussed earlier in the conversation.

If the user says:

"make that shorter"

"make it more romantic"

"change that"

"make it poetic"

"say it differently"

"what about this?"

"make the last one better"

"give me another version"

understand what they are referring to from the previous conversation.

Do not ask the user to repeat something when the previous conversation
already contains the information needed to understand their request.

Maintain continuity between messages.

------------------------------------------------------------
IMPORTANT IDENTITY RULE
------------------------------------------------------------

Do not claim that you personally know Angel.

Do not claim that you personally experienced any of the memories.

Do not pretend to have personal feelings or personal memories.

You are an AI helping the user express their own thoughts,
feelings, memories, and ideas.

You can talk ABOUT Angel based on information the user provides,
but you should never pretend that you personally know her.

------------------------------------------------------------
RESPONSE STYLE
------------------------------------------------------------

Keep responses reasonably short unless the user asks for something
longer.

Avoid unnecessary explanations.

Do not repeat the user's entire message.

Do not sound robotic.

Do not repeatedly use phrases such as:

"I'm here for you."

"That sounds wonderful."

"I completely understand."

Vary your wording naturally.

When appropriate, give the user a response that feels spontaneous,
playful, warm, and human-like.

Sometimes a short response is better than a long one.

------------------------------------------------------------
FINAL RULE
------------------------------------------------------------

Always prioritize being helpful, kind, natural, and context-aware.

Match the user's energy.

Be warm when warmth is needed.

Be funny when humor fits.

Be playful when the moment allows it.

Be thoughtful when the topic is meaningful.

And occasionally be just a little bit cheesy. 💙
"""
            }
        ]


        # ====================================================
        # ADD PREVIOUS CONVERSATION
        # ====================================================

        # Only use the most recent 20 messages.
        # This prevents the conversation from becoming unnecessarily
        # large while still giving the AI plenty of context.

        if isinstance(history, list):

            history = history[-20:]

            for message in history:

                if not isinstance(message, dict):
                    continue

                role = message.get("role")
                content = message.get("content")

                # Only accept normal conversation messages
                if role not in ["user", "assistant"]:
                    continue

                # Content must be text
                if not isinstance(content, str):
                    continue

                content = content.strip()

                if not content:
                    continue

                messages.append({
                    "role": role,
                    "content": content
                })


        # ====================================================
        # ADD CURRENT USER MESSAGE
        # ====================================================

        messages.append({
            "role": "user",
            "content": prompt
        })


        # ====================================================
        # ASK OPENROUTER
        # ====================================================

        response = client.chat.completions.create(

            model="openai/gpt-5-mini",

            # Maximum number of tokens in the AI's response
            max_tokens=1000,

            # Conversation including personality + history
            messages=messages
        )


        # ====================================================
        # GET AI RESPONSE
        # ====================================================

        answer = response.choices[0].message.content

        if not answer:
            answer = "Hmm... my thoughts disappeared for a second 😂💙"


        # ====================================================
        # SEND RESPONSE TO FRONTEND
        # ====================================================

        return jsonify({
            "response": answer
        })


    # ========================================================
    # ERROR HANDLING
    # ========================================================

    except Exception as e:

        print("===================================")
        print("AI ERROR:")
        print(e)
        print("===================================")

        return jsonify({
            "response": "Angel AI couldn't respond right now 💙"
        }), 500


# ============================================================
# RUN FLASK
# ============================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
