# 🛡️ Local Sentinel: Edge AI Cybersecurity Agent

![Status](https://img.shields.io/badge/Status-Active-success)
![AI Model](https://img.shields.io/badge/AI_Model-Qwen2.5_%2F_Phi3.5-blueviolet)
![Tech](https://img.shields.io/badge/Edge_AI-Ollama-orange)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)

**Local Sentinel** is a real-time, privacy-first cybersecurity threat detection system designed for **Edge Computing**. It eliminates the need for cloud-based security logs by using **Small Language Models (SLMs)** running locally on consumer hardware.

Unlike traditional firewalls that rely on static rules, Local Sentinel uses **Generative AI** to understand the *context* of a log entry, accurately distinguishing between a harmless error and a malicious **Brute Force** or **SQL Injection** attack.

## 🚀 Key Features

* **🧠 Local Intelligence:** Runs entirely offline using **Ollama** (Qwen 2.5 / Phi-3.5). No data leaves the network.
* **⚡ Real-Time Analysis:** Processes server logs instantly with low latency.
* **📊 Live Cyber-Dashboard:** Interactive visualization built with **Streamlit** to monitor threats in real-time.
* **🛡️ Active Defense:** Automatically detects malicious IPs and triggers a blocking mechanism (Simulated Firewall).
* **📉 Resource Optimized:** Optimized to run on standard hardware (NVIDIA RTX 3050 / 16GB RAM).

## 🛠️ Tech Stack

* **Core AI Engine:** [Ollama](https://ollama.com/) (Local Inference)
* **LLMs Used:** `qwen2.5:7b` (High Accuracy) or `phi3.5` (High Speed)
* **Backend Logic:** Python 3.10+ (Log parsing & API handling)
* **Frontend UI:** Streamlit (Real-time data visualization)
* **Simulation:** Custom Python Traffic Generator

## 📂 Project Structure

| File | Description |
| :--- | :--- |
| `sentinel.py` | **The Brain.** Monitors logs, sends data to the AI model, and executes defense logic. |
| `dashboard.py` | **The Eyes.** A Streamlit web app that visualizes attack traffic and system status. |
| `attacker.py` | **The Simulation.** Generates synthetic "Hacker" and "Safe" traffic to demonstrate the system. |
| `test_logs.txt` | The shared log file used for communication between the Attacker and the Sentinel. |

## ⚡ Installation & Setup

### 1. Prerequisites
Ensure you have **Ollama** installed and the models pulled:
```bash
ollama run qwen2.5:7b
# OR for lower memory usage
ollama run phi3.5
