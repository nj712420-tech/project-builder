# # # ai_service.py
# # import os
# # import re
# # import json
# # from openai import OpenAI
# # from e2b_code_interpreter import Sandbox
# # from dotenv import load_dotenv

# # load_dotenv()

# # # Setup the OpenRouter Client
# # client = OpenAI(
# #   base_url="https://openrouter.ai/api/v1",
# #   api_key=os.getenv("OPENROUTER_API_KEY"),
# # )

# # MODEL = "qwen/qwen-2.5-coder-32b-instruct"

# # def build_and_execute_project(prompt: str, include_db: bool):
# #     system_msg = (
# #         "You are an expert AI developer. You MUST return strictly valid JSON. "
# #         "All keys and string values MUST be enclosed in double quotes. "
# #         "Do NOT wrap the JSON in markdown blocks. "
# #         "Format your response exactly like this example:\n"
# #         "{\n"
# #         '  "explanation": "A short explanation of the code.",\n'
# #         '  "code": "def hello():\\n    print(\'Hello World\')"\n'
# #         "}"
# #     )
    
# #     if include_db:
# #         system_msg += " Include a SQLite database setup using SQLAlchemy."

# #     # 1. Generate Code
# #     response = client.chat.completions.create(
# #         model=MODEL,
# #         messages=[
# #             {"role": "system", "content": system_msg},
# #             {"role": "user", "content": prompt}
# #         ],
# #         response_format={ "type": "json_object" }
# #     )
    
# #     raw_output = response.choices[0].message.content.strip()
    
# #     # Clean the JSON
# #     match = re.search(r'\{.*\}', raw_output, re.DOTALL)
# #     if match:
# #         raw_output = match.group(0)

# #     parsed_data = json.loads(raw_output)
# #     generated_code = parsed_data.get("code", "")
# #     explanation = parsed_data.get("explanation", "")

# #     # 2. Execute Code in Sandbox
# #     execution_results = []
# #     with Sandbox.create(api_key=os.getenv("sandbox_key")) as sandbox:
# #         execution = sandbox.run_code(generated_code)
        
# #         if execution.logs.stdout:
# #             execution_results.extend(execution.logs.stdout)
# #         if execution.error:
# #             execution_results.append(f"Execution Error: {execution.error}")

# #     # 3. Return a clean dictionary to the router
# #     return {
# #         "status": "success",
# #         "explanation": explanation,
# #         "code": generated_code,
# #         "sandbox_output": "\n".join(execution_results)
# #     }


# # ai_service.py
# import os
# import re
# import json
# from openai import OpenAI
# from e2b_code_interpreter import Sandbox
# from dotenv import load_dotenv

# load_dotenv()

# client = OpenAI(
#   base_url="https://openrouter.ai/api/v1",
#   api_key=os.getenv("OPENROUTER_API_KEY"),
# )

# MODEL = "qwen/qwen-2.5-coder-32b-instruct"

# def build_and_execute_project(prompt: str, include_db: bool):
#     # 1. UPDATE THE PROMPT: Demand a Flask Web App
#     system_msg = (
#         "You are an expert developer. You MUST return strictly valid JSON. "
#         "Write a complete, single-file Python Flask web application. "
#         "The Flask app MUST run on port 5000 and bind to host '0.0.0.0'. "
#         "Include all HTML, CSS, and JS inside the Flask route as a single Python string. "
#         "CRITICAL JSON RULES: "
#         "1. You MUST properly escape ALL newlines as \\n inside the code string. "
#         "2. You MUST properly escape ALL double quotes as \\\" inside the code string. "
#         "3. DO NOT use render_template_string or Jinja syntax. "
#         "4. Write normal JS/CSS without double-escaping curly braces. "
#         "Format exactly like this:\n"
#         "{\n"
#         '  "explanation": "Flask app with HTML.",\n'
#         '  "code": "from flask import Flask\\napp = Flask(__name__)\\n@app.route(\'/\')\\ndef home():\\n    html=\'<h1 style=\\\"color:red;\\\">Hi</h1>\'\\n    return html\\nif __name__ == \'__main__\':\\n    app.run(host=\'0.0.0.0\', port=5000)"\n'
#         "}"
#     )
    
#     if include_db:
#         system_msg += " Include a SQLite database setup using SQLAlchemy."

#     # 2. Get Code from AI
#     response = client.chat.completions.create(
#         model=MODEL,
#         messages=[
#             {"role": "system", "content": system_msg},
#             {"role": "user", "content": prompt}
#         ],
#         response_format={ "type": "json_object" },
#         max_tokens = 3000
#     )
    
#     raw_output = response.choices[0].message.content.strip()
#     print(raw_output)
#     match = re.search(r'\{.*\}', raw_output, re.DOTALL)
#     if match:
#         raw_output = match.group(0)

#     parsed_data = json.loads(raw_output)
#     generated_code = parsed_data.get("code", "")
#     explanation = parsed_data.get("explanation", "")

#     # 3. THE BIG CHANGE: Booting the Web Server
#     # We remove the `with` statement so the sandbox stays alive!
#     sandbox = Sandbox.create(api_key=os.getenv("sandbox_key"))
    
#     # Step A: Write the AI's code to a file in the sandbox
#     sandbox.files.write("app.py", generated_code)
    
#     # Step B: Install Flask
#     sandbox.commands.run("pip install flask")
    
#     # Step C: Run the server in the background so our API doesn't freeze
#     sandbox.commands.run("python app.py", background=True)
    
#     # Step D: Get the public URL for port 5000
#     preview_url = sandbox.get_host(5000)

#     return {
#         "status": "success",
#         "explanation": explanation,
#         "code": generated_code,
#         "preview_url": preview_url  # <-- We send this URL to the frontend!
#     }

import os
import re
import time
from openai import OpenAI
from e2b_code_interpreter import Sandbox
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("OPENROUTER_API_KEY"),
)

MODEL = "qwen/qwen-2.5-coder-32b-instruct"

def build_and_execute_project(prompt: str, include_db: bool):
    # 1. NEW PROMPT: Use Tags instead of JSON for bulletproof looping
    system_msg = (
        "You are an expert developer. "
        "Write a complete Python Flask web application. "
        "The Flask app MUST run on port 5000 and bind to host '0.0.0.0'. "
        "Include all HTML, CSS, and JS inside the Flask route as a Python string. "
        "DO NOT USE JSON. You MUST use these exact tags to separate your response:\n\n"
        "[EXPLANATION]\nWrite your short explanation here.\n[/EXPLANATION]\n\n"
        "[CODE]\nfrom flask import Flask\n...rest of code...\n[/CODE]"
    )
    
    if include_db:
        system_msg += " Include a SQLite database setup using SQLAlchemy."

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": prompt}
    ]

    full_response = ""
    
    # 2. THE LOOP: Run up to 3 times to get all the code
    for chunk_number in range(1, 4):
        print(f"⏳ Generation Round {chunk_number}...")
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=1500 # Safe limit for the free tier
        )
        
        chunk_text = response.choices[0].message.content
        finish_reason = response.choices[0].finish_reason
        
        full_response += chunk_text
        
        if finish_reason == "stop" or finish_reason != "length":
            print("✅ AI finished generating code!")
            break # The AI is completely done, break the loop!
            
        print("⚠️ Token limit reached. Asking AI to continue...")
        # Tell the AI to remember what it just said, and ask it to keep going
        messages.append({"role": "assistant", "content": chunk_text})
        messages.append({"role": "user", "content": "Continue exactly where you left off. Do not repeat anything. Do not add intro text."})

    # 3. EXTRACT THE DATA USING REGEX (Goodbye JSON errors!)
    explanation = "No explanation provided."
    generated_code = ""

    exp_match = re.search(r'\[EXPLANATION\](.*?)\[/EXPLANATION\]', full_response, re.DOTALL | re.IGNORECASE)
    if exp_match:
        explanation = exp_match.group(1).strip()

    code_match = re.search(r'\[CODE\](.*?)\[/CODE\]', full_response, re.DOTALL | re.IGNORECASE)
    if code_match:
        generated_code = code_match.group(1).strip()
    else:
        # Fallback just in case it forgets the closing tag
        generated_code = full_response.replace("[CODE]", "").strip()

    # 4. BOOT THE WEB SERVER IN THE CLOUD
    try:
        print("🚀 Booting E2B Sandbox...")
        sandbox = Sandbox.create(api_key=os.getenv("sandbox_key"))

        print("writing code to app.py")
        sandbox.files.write("app.py", generated_code)

        print("installing framework")
        sandbox.commands.run("pip install flask")

        sandbox.commands.run("python app.py > server.log 2>&1", background=True)

        time.sleep(5)

        try:
            server_logs = sandbox.files.read("server.log")
            print("--- FLASK SERVER LOGS ---")
            print(server_logs)
        except Exception:
            server_logs = "Could not read server logs."
            
        preview_url = sandbox.get_host(5000)

        return {
            "status": "success",
            "explanation": explanation,
            "code": generated_code,
            "preview_url": preview_url,
            "sandbox_output": server_logs

        }
    except Exception as e:
        return {"status": "error", "error": str(e)}