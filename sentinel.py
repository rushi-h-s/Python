import re
import time
import requests
import json
import os
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
import subprocess

def block_ip(ip):
    """The kill SWITCH to block malicious IPs using system firewall rules"""
    if ip == "127.0.0.1":  # FIXED: Removed backtick
        # Simulation mode
        print(f"🚫 [FIREWALL] BLOCKING IP: {ip}")
        return True
    
    # Add actual blocking logic here for real IPs
    try:
        # Example for Windows (requires admin):
        # subprocess.run(["netsh", "advfirewall", "firewall", "add", "rule", 
        #                 f"name=Block_{ip}", "dir=in", "action=block", 
        #                 f"remoteip={ip}"], check=True)
        
        # For now, just log it
        print(f"🚫 [FIREWALL] Would block IP: {ip}")
        return True
    except Exception as e:
        print(f"❌ Failed to block {ip}: {e}")
        return False

# --- CONFIGURATION ---
LOG_FILE_PATH = "test_logs.txt" 
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "phi3.5"

console = Console()

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = """
You are a cybersecurity sentinel. Analyze the log line for threats like SSH Brute Force, SQL Injection, or XSS.
Return JSON ONLY. No explanation.
Format: {"malicious": true/false, "confidence": 0-100, "type": "attack_name", "ip": "1.2.3.4"}
"""

def analyze_log_line(log_line):
    if not log_line.strip():
        return None

    # 1. Python Extracts the IP (100% Accuracy)
    ip_match = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", log_line)
    extracted_ip = ip_match.group(1) if ip_match else None

    # 2. AI Analyzes the Threat
    payload = {
        "model": MODEL_NAME,
        "prompt": f"LOG: {log_line}",
        "system": SYSTEM_PROMPT,
        "stream": False,
        "format": "json"
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=10)
        response.raise_for_status()
        response_json = response.json()
        ai_result = json.loads(response_json['response'])

        # 3. MERGE: Use AI's logic + Python's IP
        ai_result['ip'] = extracted_ip 
        return ai_result

    except requests.exceptions.RequestException as e:
        return {"error": f"API Error: {str(e)}", "malicious": False}
    except json.JSONDecodeError as e:
        return {"error": f"JSON Parse Error: {str(e)}", "malicious": False}
    except Exception as e:
        return {"error": str(e), "malicious": False}

def follow(file):
    """Windows-compatible 'tail -f' to read new lines instantly."""
    file.seek(0, 2)  # Go to the end of the file
    while True:
        line = file.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line

def main():
    # 1. Create the dummy log file if it doesn't exist
    if not os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, "w", encoding="utf-8") as f:
            f.write("System started...\n")

    console.print(Panel(
        f"[bold green]Sentinel Active[/bold green]\n"
        f"Target: {LOG_FILE_PATH}\n"
        f"Model: {MODEL_NAME}"
    ))
    console.print("[yellow]Waiting for new logs... (Open 'test_logs.txt' and add lines to test)[/yellow]")

    try:
        with open(LOG_FILE_PATH, "r", encoding="utf-8") as logfile:
            for line in follow(logfile):
                line = line.strip()
                if not line:
                    continue
                
                console.print(f"\n[dim]Received:[/dim] {line}")
                
                # Send to AI
                with console.status("[bold cyan]Analyzing...[/bold cyan]"):
                    start_time = time.time()
                    result = analyze_log_line(line)
                    end_time = time.time()
                
                # Display Result
                if result and result.get("malicious"):
                    console.print(Panel(
                        f"[bold red]THREAT DETECTED[/bold red]\n"
                        f"Type: {result.get('type', 'Unknown')}\n"
                        f"IP: {result.get('ip', 'N/A')}\n"
                        f"Confidence: {result.get('confidence', 0)}%\n"
                        f"Speed: {round(end_time - start_time, 2)}s",
                        border_style="red"
                    ))
                    if result.get('ip'):
                        block_ip(result.get("ip"))
                elif result and result.get("error"):
                    console.print(f"[yellow]⚠ Error: {result.get('error')}[/yellow]")
                else:
                    console.print(f"[green]✔ Safe[/green] ({round(end_time - start_time, 2)}s)")

    except KeyboardInterrupt:
        console.print("\n[red]Sentinel Stopped[/red]")
    except Exception as e:
        console.print(f"[red]Fatal Error: {e}[/red]")

if __name__ == "__main__":
    main()