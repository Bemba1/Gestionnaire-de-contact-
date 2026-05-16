import urllib.request
import json
import ssl

url = "https://mnrowmfzdsahzeindnve.supabase.co/rest/v1/contacts_list"

headers = {
    "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1ucm93bWZ6ZHNhaHplaW5kbnZlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzcxOTc0NDIsImV4cCI6MjA5Mjc3MzQ0Mn0.v7tG1tvzBtU_fBIItxPM0bNB4GrE15hb7A877SxBdt8",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1ucm93bWZ6ZHNhaHplaW5kbnZlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzcxOTc0NDIsImV4cCI6MjA5Mjc3MzQ0Mn0.v7tG1tvzBtU_fBIItxPM0bNB4GrE15hb7A877SxBdt8"
}

# ⚠️ désactive SSL (temporaire)
context = ssl._create_unverified_context()

req = urllib.request.Request(url, headers=headers)

with urllib.request.urlopen(req, context=context) as response:
    raw = response.read().decode()
    
    print("=== RÉPONSE BRUTE ===")
    print(raw)
    
    try:
        data = json.loads(raw)
        print("=== JSON PARSÉ ===")
        print(data)
    except json.JSONDecodeError:
        print("⚠️ La réponse n'est pas du JSON valide")