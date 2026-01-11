import time
import random
import os
import sys

print("="*60)
print("🚀 ATTACKER SCRIPT STARTING...")
print("="*60)

# CONFIG
LOG_FILE = "test_logs.txt"

try:
    # Test if we can write to the file
    print(f"📁 Checking file access: {LOG_FILE}")
    
    # Create or verify file exists
    if not os.path.exists(LOG_FILE):
        print("   Creating new log file...")
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("=== Attack Simulation Started ===\n")
        print("   ✅ File created successfully")
    else:
        print("   ✅ File exists")
    
    # ATTACK TEMPLATES
    attacks = [
        "Failed password for root from 192.168.1.{} port 22 ssh2",
        "Failed password for admin from 10.0.0.{} port 22 ssh2",
        "Invalid user guest from 172.16.0.{} port 443",
        "SQL injection attempt detected from 203.0.113.{} - SELECT * FROM users WHERE id=1 OR 1=1",
        "XSS attack blocked from 198.51.100.{} - <script>alert('hacked')</script>",
        "Multiple failed login attempts from 192.0.2.{} - BRUTE FORCE DETECTED"
    ]

    safe_logs = [
        "Accepted password for ubuntu from 192.168.1.50 port 22 ssh2",
        "Disconnected from 192.168.1.50 port 22",
        "Connection closed by 127.0.0.1 port 80",
        "GET /api/health 200 from 10.0.0.5",
        "User login successful from 192.168.1.100",
        "Normal traffic from 172.16.0.20"
    ]

    print("\n⚙️  CONFIGURATION:")
    print(f"   📂 Log file: {LOG_FILE}")
    print(f"   🎲 Attack probability: 40%")
    print(f"   ⏱️  Interval: 3 seconds")
    print(f"   📊 Attack types: {len(attacks)}")
    print(f"   📊 Safe types: {len(safe_logs)}")
    
    print("\n" + "="*60)
    print("🔴 = Attack | 🟢 = Safe")
    print("Press CTRL+C to stop")
    print("="*60 + "\n")

    log_count = 0

    while True:
        log_count += 1
        
        # 40% chance of attack
        if random.random() < 0.4:
            # Generate attack log
            log = attacks[random.randint(0, len(attacks)-1)].format(random.randint(1, 255))
            symbol = "🔴"
            log_type = "ATTACK"
        else:
            # Generate safe log
            log = safe_logs[random.randint(0, len(safe_logs)-1)]
            symbol = "🟢"
            log_type = "SAFE  "

        # Print to console
        print(f"[{log_count:03d}] {symbol} {log_type}: {log[:70]}...")
        
        # Write to file
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(log + "\n")
                f.flush()
            
            # Verify write
            if log_count % 10 == 0:
                file_size = os.path.getsize(LOG_FILE)
                print(f"      📝 File size: {file_size} bytes")
                
        except Exception as write_error:
            print(f"❌ ERROR writing to file: {write_error}")
            break

        time.sleep(3)

except KeyboardInterrupt:
    print("\n\n" + "="*60)
    print("🛑 ATTACKER STOPPED BY USER")
    print(f"📊 Total logs generated: {log_count}")
    print("="*60)
    
except Exception as e:
    print("\n\n" + "="*60)
    print(f"❌ FATAL ERROR: {type(e).__name__}")
    print(f"   Message: {str(e)}")
    print("="*60)
    import traceback
    traceback.print_exc()
    
finally:
    print("\nPress Enter to exit...")
    input()