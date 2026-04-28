import os
import warnings

# Suppress the deprecation warning from google-generativeai
warnings.filterwarnings("ignore", category=FutureWarning)

import google.generativeai as genai
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print("\n--- Diagnostic: Available Gemini Models ---")
    try:
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        print("Models you can use:", available)
    except Exception as e:
        print("Could not fetch models:", e)
    print("-------------------------------------------\n")

# Initialize HuggingFace Client
hf_client = InferenceClient(api_key=HUGGINGFACE_API_KEY) if HUGGINGFACE_API_KEY else None

# Models Fallback Chains
GEMINI_MODELS = [
    'gemini-3.1-flash-lite-preview',
    'gemini-flash-lite-latest',
    'gemini-flash-latest'
]

HUGGINGFACE_MODELS = [
    'microsoft/Phi-3-mini-4k-instruct',
    'HuggingFaceH4/zephyr-7b-beta'
]

def extract_with_gemini(email_body, system_instruction, model_name):
    if not GEMINI_API_KEY:
        raise ValueError("Gemini API key is not set.")
        
    model = genai.GenerativeModel(
        model_name,
        system_instruction=system_instruction
    )
    response = model.generate_content(email_body)
    return response.text.strip()

def extract_with_huggingface(email_body, system_instruction, model_name):
    if not hf_client:
        raise ValueError("HuggingFace API key is not set.")
        
    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": f"Please process this email:\n\n{email_body}"}
    ]
    
    response = hf_client.chat_completion(
        messages=messages,
        model=model_name,
        max_tokens=800,
        temperature=0.5
    )
    return response.choices[0].message.content.strip()

def extract_actionable_tasks(email_body):
    system_instruction = (
        "You are a highly efficient assistant. Your job is to read incoming emails and provide a brief, crisp analysis for a WhatsApp message.\n"
        "Format your response EXACTLY like this:\n\n"
        "📝 *Quick Summary:*\n"
        "(1-2 short sentences capturing the main point of the email)\n\n"
        "✅ *Actionable Tasks:*\n"
        "- (Extract a clear, concise bulleted list of tasks. If no tasks exist, write 'No actionable tasks found.')\n\n"
        "Keep the entire response as short, direct, and actionable as possible. Do NOT repeat the full email content."
    )
    
    # 1. Try Gemini Models first
    for model in GEMINI_MODELS:
        try:
            print(f"Attempting extraction with Gemini ({model})...")
            return extract_with_gemini(email_body, system_instruction, model)
        except Exception as e:
            print(f"  -> Failed: {e}")

    # 2. Try HuggingFace Models if all Gemini models fail
    for model in HUGGINGFACE_MODELS:
        try:
            print(f"Attempting extraction with HuggingFace ({model})...")
            return extract_with_huggingface(email_body, system_instruction, model)
        except Exception as e:
            print(f"  -> Failed: {e}")

    print("❌ All AI models (Gemini & HuggingFace) failed.")
    return None
