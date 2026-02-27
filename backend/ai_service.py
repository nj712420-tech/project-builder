# import os
# import re
# import time
# from openai import OpenAI
# from e2b_code_interpreter import Sandbox
# from dotenv import load_dotenv

# load_dotenv()

# # Initialize API Clients
# client = OpenAI(
#   base_url="https://openrouter.ai/api/v1",
#   api_key=os.getenv("OPENROUTER_API_KEY"),
# )

# # Use the E2B key from .env (Look for both common names)
# e2b_key = os.getenv("sandbox_key") or os.getenv("E2B_API_KEY")
# if not e2b_key:
#     raise Exception("❌ E2B API Key is missing! Check your .env file.")

# MODEL = "google/gemini-2.5-flash-lite-preview-09-2025"

# def build_and_execute_project(prompt: str, include_db: bool):
#     # 1. PROMPT: Use Tags for safe extraction
#     system_msg = (
#         "You are an expert full-stack developer. "
#         "Write a complete Python Flask web application. "
#         "The Flask app MUST run on port 5000 and bind to host '0.0.0.0'. "
#         "Include all HTML, CSS, and JS inside the Flask route as a standard Python string. "
        
#         "CRITICAL SYNTAX RULES:"
#         "1. DO NOT use f-strings (f''') for the HTML content. Use standard triple quotes (''')."
#         "2. DO NOT use Jinja2 templating syntax (no {{ }} or {% %}). Python will crash."
#         "3. Handle ALL dynamic logic (like toggling Dark Mode or updating Charts) using client-side JavaScript (document.getElementById, event listeners), NOT server-side logic."
        
#         "DO NOT USE JSON. You MUST use these exact tags to separate your response:\n\n"
#         "[EXPLANATION]\nWrite your short explanation here.\n[/EXPLANATION]\n\n"
#         "[CODE]\nfrom flask import Flask\n...rest of code...\n[/CODE]"
#     )
    
#     if include_db:
#         system_msg += " Include a SQLite database setup using SQLAlchemy."

#     messages = [
#         {"role": "system", "content": system_msg},
#         {"role": "user", "content": prompt}
#     ]

#     full_response = ""
    
#     # 2. THE LOOP: Robust 5-Round limit
#     for chunk_number in range(1, 6):
#         print(f"⏳ Generation Round {chunk_number}...")
#         try:
#             response = client.chat.completions.create(
#                 model=MODEL,
#                 messages=messages,
#                 max_tokens=2000, 
#                 temperature=0.7
#             )
            
#             # --- DEFENSIVE CHECK 1: Did the API return garbage? ---
#             if not response or not response.choices:
#                 print("⚠️ API returned empty response. Retrying round...")
#                 time.sleep(1) # Wait a bit before retrying
#                 continue
            
#             chunk_text = response.choices[0].message.content
#             if not chunk_text:
#                 print("⚠️ API returned empty text. Retrying round...")
#                 continue
                
#             # Handle "None" finish_reason (Common OpenRouter quirk)
#             finish_reason = response.choices[0].finish_reason or "length" 
            
#             full_response += chunk_text
            
#             # If the AI is done, break the loop
#             if finish_reason == "stop" or finish_reason == "end_turn":
#                 print("✅ AI finished generating code!")
#                 break 
                
#             print(f"⚠️ Token limit reached (Reason: {finish_reason}). Asking AI to continue...")
            
#             # Append the previous answer so the AI knows what it wrote
#             messages.append({"role": "assistant", "content": chunk_text})
#             messages.append({"role": "user", "content": "Continue exactly where you left off. Do not repeat code."})
            
#         except Exception as e:
#             print(f"❌ Error during generation round {chunk_number}: {e}")
#             # Don't break! Try to use what we have so far.
#             break

#     # 3. SMARTER EXTRACTION
#     explanation = "No explanation provided."
#     generated_code = ""

#     # Extract Explanation
#     exp_match = re.search(r'\[EXPLANATION\](.*?)\[/EXPLANATION\]', full_response, re.DOTALL | re.IGNORECASE)
#     if exp_match:
#         explanation = exp_match.group(1).strip()

#     # Extract Code - Improved Fallback Logic
#     code_match = re.search(r'\[CODE\](.*?)\[/CODE\]', full_response, re.DOTALL | re.IGNORECASE)
#     if code_match:
#         generated_code = code_match.group(1).strip()
#     else:
#         # FALLBACK: If [/CODE] is missing, grab everything AFTER [CODE]
#         parts = full_response.split("[CODE]")
#         if len(parts) > 1:
#             generated_code = parts[1].strip()
#         else:
#             generated_code = full_response.strip()

#     # Clean up Markdown (backticks) if present
#     generated_code = generated_code.replace("```python", "").replace("```html", "").replace("```", "").strip()

#     # 4. BOOT THE WEB SERVER IN THE CLOUD
#     try:
#         print("🚀 Booting E2B Sandbox...")
#         sandbox = Sandbox.create(api_key=e2b_key)
        
#         print("📝 Writing code to app.py...")
#         sandbox.files.write("app.py", generated_code)
        
#         print("📦 Installing Flask...")
#         sandbox.commands.run("pip install flask")
        
#         print("🏃 Starting Flask server & capturing logs...")
#         sandbox.commands.run("python app.py > server.log 2>&1", background=True)
        
#         # Wait for Flask to boot
#         print("⏳ Waiting for server to stabilize...")
#         time.sleep(3) 
        
#         # Read logs to catch syntax errors
#         server_logs = "No logs available."
#         try:
#             server_logs = sandbox.files.read("server.log")
#             print("--- FLASK SERVER LOGS ---")
#             print(server_logs)
#         except Exception:
#             pass

#         preview_url = sandbox.get_host(5000)

#         return {
#             "status": "success",
#             "explanation": explanation,
#             "code": generated_code,
#             "preview_url": preview_url,
#             "sandbox_output": server_logs
#         }
#     except Exception as e:
#         return {"status": "error", "error": str(e)}


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

# Using Gemini 2.0 Flash for speed and context
MODEL = "google/gemini-2.5-flash-lite-preview-09-2025"

def build_and_execute_project(prompt: str, include_db: bool):
    # 1. NEW PROMPT: LANGUAGE AGNOSTIC
    system_msg = (
        "You are an expert Full-Stack Architect. "
        "Analyze the user's request and choose the best language (Node.js, Python, Go, etc.). "
        
        "CRITICAL RULES: "
        "1. You MUST generate a file named 'setup.sh'. This script must: \n"
        "   - Install dependencies (e.g., 'npm install', 'pip install', 'go mod init myapp && go get'). \n"
        "   - START the server in the foreground (do not use '&' or 'nohup'). \n"
        "2. The server application MUST listen on HOST '0.0.0.0' and PORT 5000. \n"
        "   - DO NOT use localhost, 127.0.0.1, port 8080, or port 3000. \n"
        "3. Language Specific Listen Commands (YOU MUST USE THESE EXACTLY): \n"
        "   - Node.js/Express: `app.listen(5000, '0.0.0.0', ...)` \n"
        "   - Python/Flask: `app.run(host='0.0.0.0', port=5000)` \n"
        "   - Go (Golang): `http.ListenAndServe(\":5000\", nil)` \n"
        "4. Use <file name='filename'>...code...</file> tags for every single file. \n"
        "5. Example setup.sh for Go: \n"
        "   go mod init myapp \n"
        "   go mod tidy \n"
        "   go run main.go \n"
    )
    
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": prompt}
    ]

    full_response = ""
    
    # 2. GENERATION LOOP
    for chunk_number in range(1, 6):
        print(f"⏳ Generation Round {chunk_number}...")
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                max_tokens=4000,
                temperature=0.7
            )
            
            if not response or not response.choices:
                continue
            
            chunk_text = response.choices[0].message.content
            full_response += chunk_text
            
            finish_reason = response.choices[0].finish_reason
            if finish_reason == "stop" or finish_reason == "end_turn":
                print("✅ AI finished generating code!")
                break 
                
            messages.append({"role": "assistant", "content": chunk_text})
            messages.append({"role": "user", "content": "Continue exactly where you left off."})
            
        except Exception as e:
            print(f"❌ Error: {e}")
            break

    # 3. PARSING: Robust Logic
    files = {}
    explanation = "No explanation provided."

    # Extract explanation
    exp_match = re.search(r'\[EXPLANATION\](.*?)\[/EXPLANATION\]', full_response, re.DOTALL | re.IGNORECASE)
    if exp_match:
        explanation = exp_match.group(1).strip()

    # Extract files
    file_pattern = re.compile(r'<file name=[\'"](.*?)[\'"]>(.*?)</file>', re.DOTALL | re.IGNORECASE)
    
    for match in file_pattern.finditer(full_response):
        filename = match.group(1).strip()
        code_content = match.group(2).strip()
        
        # CLEANUP: Remove markdown code blocks if the AI added them
        code_content = re.sub(r'^```[a-z]*\n', '', code_content, flags=re.MULTILINE)
        code_content = re.sub(r'\n```$', '', code_content, flags=re.MULTILINE)
        
        files[filename] = code_content
    
    if "setup.sh" not in files:
        # Fallback if AI forgot setup.sh (forces Python default)
        print("⚠️ AI forgot setup.sh, creating fallback...")
        files["setup.sh"] = "pip install flask\npython app.py > server.log 2>&1"

    # 4. EXECUTION: The Universal Runner
    try:
        e2b_key = os.getenv("sandbox_key")
        print("🚀 Booting E2B Sandbox...")
        sandbox = Sandbox.create(api_key=e2b_key)
        
        # Write files
        for fname, fcontent in files.items():
            if "/" in fname:
                folder = fname.rsplit("/", 1)[0]
                sandbox.commands.run(f"mkdir -p {folder}")
            sandbox.files.write(fname, fcontent)
        
        print("🛠️ Installing & Starting Server...")
        
        # Make script executable
        sandbox.commands.run("chmod +x setup.sh")
        
        # Run the generic setup script
        sandbox.commands.run("sh ./setup.sh", background=True)
        
        # Wait longer for Node/Go builds
        time.sleep(10) 
        
        # Read Logs
        server_logs = "No logs."
        try:
            server_logs = sandbox.files.read("server.log")
        except: pass

        # GET PREVIEW URL (With Protocol Fix)
        host = sandbox.get_host(5000)
        preview_url = f"https://{host}"  # Force HTTPS to prevent local inception
        print("preview url", preview_url)

        return {
            "status": "success",
            "explanation": explanation,
            "files": files,
            "preview_url": preview_url,
            "sandbox_output": server_logs
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}