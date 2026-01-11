import re
import time
import requests
import json
import os
from rich.console import Console
from rich.panel import Panel

def block_ip(ip):
    """The kill SWITCH to block malicious IPs"""
    if not ip or ip == "N/A":
        return False
    
    print(f"🚫 [FIREWALL] BLOCKING IP: {ip}")
    return True

# --- CONFIGURATION ---
LOG_FILE_PATH = "test_logs.txt" 
OLLAMA_API_URL = "http://localhost:11434/api/generate"

# IMPORTANT: Change this to match your actual Ollama model!
MODEL_NAME = "qwen2.5:7b"  # Changed from phi3.5 to match your system

console = Console()

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = """
You are a cybersecurity AI. Analyze this log for threats like:
- SSH brute force (multiple failed passwords)
- SQL injection (SQL keywords in URLs)
- XSS attacks (script tags, malicious code)
- Invalid/suspicious user attempts

Respond ONLY with valid JSON in this exact format:
{"malicious": true, "confidence": 95, "type": "SSH Brute Force", "ip": "192.168.1.1"}

If safe, respond:
{"malicious": false, "confidence": 90, "type": "Normal Traffic", "ip": "192.168.1.1"}
"""

def analyze_log_line(log_line):
    if not log_line.strip() or log_line.strip().startswith("==="):
        return None

    # 1. Extract IP from log
    ip_match = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", log_line)
    extracted_ip = ip_match.group(1) if ip_match else "N/A"

    # 2. Send to Ollama
    payload = {
        "model": MODEL_NAME,
        "prompt": f"Analyze this log:\n{log_line}\n\nRespond ONLY with JSON.",
        "system": SYSTEM_PROMPT,
        "stream": False,
        "format": "json"
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=15)
        response.raise_for_status()
        
        response_json = response.json()
        ai_text = response_json.get('response', '{}')
        
        # Clean up response (remove markdown if present)
        ai_text = ai_text.strip()
        if ai_text.startswith('```'):
            ai_text = ai_text.split('```')[1]
            if ai_text.startswith('json'):
                ai_text = ai_text[4:]
        
        ai_result = json.loads(ai_text)
        
        # Merge AI result with extracted IP
        ai_result['ip'] = extracted_ip 
        return ai_result

    except requests.exceptions.Timeout:
        return {"error": "Ollama timeout - is it running?", "malicious": False}
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to Ollama - check if running on port 11434", "malicious": False}
    except json.JSONDecodeError as e:
        return {"error": f"AI returned invalid JSON: {e}", "malicious": False}
    except Exception as e:
        return {"error": str(e), "malicious": False}

def follow(file):
    """Real-time log following (works on Windows)"""
    file.seek(0, 2)  # Jump to end
    while True:
        line = file.readline()
        if not line:
            time.sleep(0.2)  # Check every 200ms
            continue
        yield line

def main():
    # Create log file if missing
    if not os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, "w", encoding="utf-8") as f:
            f.write("Sentinel Active\n")

    console.print(Panel(
        f"[bold green]Sentinel Active[/bold green]\n"
        f"Target: {LOG_FILE_PATH}\n"
        f"Model: {MODEL_NAME}\n"
        f"API: {OLLAMA_API_URL}",
        style="green"
    ))
    
    console.print("[yellow]Waiting for new logs... (Run attacker.py to generate traffic)[/yellow]\n")

    # Test Ollama connection
    try:
        test_response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if test_response.status_code == 200:
            console.print("[green]✓ Ollama connected successfully[/green]\n")
        else:
            console.print("[red]⚠ Ollama connection issue[/red]\n")
    except:
        console.print("[red]⚠ Cannot reach Ollama! Start it with: ollama serve[/red]\n")

    processed = 0
    
    try:
        with open(LOG_FILE_PATH, "r", encoding="utf-8", errors="ignore") as logfile:
            for line in follow(logfile):
                line = line.strip()
                if not line or line.startswith("==="):
                    continue
                
                processed += 1
                console.print(f"\n[bold cyan]>>> Log #{processed}:[/bold cyan] [dim]{line[:80]}...[/dim]")
                
                # Analyze with AI
                with console.status("[bold yellow]🤖 AI analyzing...[/bold yellow]"):
                    start = time.time()
                    result = analyze_log_line(line)
                    elapsed = time.time() - start
                
                # Show results
                if not result:
                    continue
                    
                if result.get("error"):
                    console.print(f"[yellow]⚠ {result['error']}[/yellow]")
                    continue
                
                if result.get("malicious"):
                    console.print(Panel(
                        f"[bold red]🚨 THREAT DETECTED 🚨[/bold red]\n\n"
                        f"Type: [bold]{result.get('type', 'Unknown')}[/bold]\n"
                        f"IP: [bold]{result.get('ip', 'N/A')}[/bold]\n"
                        f"Confidence: [bold]{result.get('confidence', 0)}%[/bold]\n"
                        f"Analysis time: {elapsed:.2f}s",
                        border_style="red",
                        style="on red"
                    ))
                    
                    if result.get('ip') != "N/A":
                        block_ip(result['ip'])
                else:
                    console.print(
                        f"[green]✅ Safe[/green] "
                        f"(Confidence: {result.get('confidence', 0)}%, "
                        f"Time: {elapsed:.2f}s)"
                    )

    except KeyboardInterrupt:
        console.print(f"\n\n[bold red]🛑 Sentinel Stopped[/bold red]")
        console.print(f"[dim]Total logs processed: {processed}[/dim]")

if __name__ == "__main__":
    main()