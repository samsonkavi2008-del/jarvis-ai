from flask import Flask, request, jsonify, render_template_string
from groq import Groq
import datetime

app = Flask(__name__)
client = Groq(api_key="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")

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>JARVIS</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial; text-align: center; background: #000510; color: #00d4ff; min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 20px; }
        h1 { color: #00d4ff; font-size: 36px; margin-bottom: 5px; text-shadow: 0 0 20px #00d4ff; letter-spacing: 10px; }
        h3 { color: #0088ff; font-size: 14px; margin-bottom: 20px; letter-spacing: 5px; }
        #status { font-size: 14px; color: #0088ff; margin: 10px; min-height: 20px; }
        #ring { width: 160px; height: 160px; border-radius: 50%; border: 3px solid #00d4ff; display: flex; align-items: center; justify-content: center; margin: 20px auto; box-shadow: 0 0 30px #00d4ff, inset 0 0 30px rgba(0,212,255,0.1); position: relative; cursor: pointer; }
        #ring.listening { border-color: #ff4444; box-shadow: 0 0 40px #ff4444, inset 0 0 30px rgba(255,68,68,0.1); animation: pulse 1s infinite; }
        #ring.thinking { border-color: #ffaa00; box-shadow: 0 0 40px #ffaa00; animation: spin 2s linear infinite; }
        #ring.speaking { border-color: #00ff88; box-shadow: 0 0 40px #00ff88; animation: pulse 0.5s infinite; }
        @keyframes pulse { 0%,100% { transform: scale(1); } 50% { transform: scale(1.05); } }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        #micBtn { background: transparent; border: none; color: #00d4ff; font-size: 50px; cursor: pointer; }
        #result { background: rgba(0,212,255,0.05); border: 1px solid rgba(0,212,255,0.3); padding: 15px; border-radius: 10px; margin: 10px; font-size: 15px; min-height: 60px; width: 100%; max-width: 400px; line-height: 1.6; color: white; }
        #wakeBtn { background: transparent; border: 1px solid #00d4ff; color: #00d4ff; padding: 8px 20px; border-radius: 20px; cursor: pointer; font-size: 13px; margin: 5px; }
        #wakeBtn.active { background: rgba(0,212,255,0.2); box-shadow: 0 0 10px #00d4ff; }
        #history { width: 100%; max-width: 400px; margin-top: 10px; max-height: 200px; overflow-y: auto; }
        .msg { padding: 8px 12px; border-radius: 8px; margin: 4px 0; font-size: 13px; text-align: left; }
        .msg.user { background: rgba(0,136,255,0.1); border-left: 3px solid #0088ff; color: #88ccff; }
        .msg.ai { background: rgba(0,212,255,0.1); border-left: 3px solid #00d4ff; color: #00d4ff; }
        .commands { display: grid; grid-template-columns: 1fr 1fr; gap: 5px; margin: 10px; width: 100%; max-width: 400px; }
        .cmd { background: rgba(0,212,255,0.05); border: 1px solid rgba(0,212,255,0.2); color: #00d4ff; padding: 8px; border-radius: 8px; font-size: 11px; cursor: pointer; }
        .cmd:active { background: rgba(0,212,255,0.2); }
    </style>
</head>
<body>
    <h1>J.A.R.V.I.S</h1>
    <h3>JUST A RATHER VERY INTELLIGENT SYSTEM</h3>
    <p id="status">Initializing systems...</p>

    <div id="ring" onclick="startListening()">
        <button id="micBtn">🎤</button>
    </div>

    <button id="wakeBtn" onclick="toggleWake()">((•)) Say "Hey Jarvis"</button>

    <div id="result">All systems ready. How can I help you?</div>

    <div class="commands">
        <div class="cmd" onclick="sendCommand('open youtube')">📺 YouTube</div>
        <div class="cmd" onclick="sendCommand('open whatsapp')">💬 WhatsApp</div>
        <div class="cmd" onclick="sendCommand('open chrome')">🌐 Chrome</div>
        <div class="cmd" onclick="sendCommand('open camera')">📷 Camera</div>
        <div class="cmd" onclick="sendCommand('open settings')">⚙️ Settings</div>
        <div class="cmd" onclick="sendCommand('open instagram')">📸 Instagram</div>
        <div class="cmd" onclick="sendCommand('what time is it')">🕐 Time</div>
        <div class="cmd" onclick="sendCommand('tell me a joke')">😄 Joke</div>
    </div>

    <div id="history"></div>

    <script>
        // App packages for opening
        const appPackages = {
            'youtube': 'com.google.android.youtube',
            'whatsapp': 'com.whatsapp',
            'chrome': 'com.android.chrome',
            'camera': 'com.android.camera',
            'settings': 'com.android.settings',
            'instagram': 'com.instagram.android',
            'facebook': 'com.facebook.katana',
            'twitter': 'com.twitter.android',
            'gmail': 'com.google.android.gm',
            'maps': 'com.google.android.apps.maps',
            'calculator': 'com.android.calculator2',
            'clock': 'com.android.deskclock',
            'spotify': 'com.spotify.music',
            'telegram': 'org.telegram.messenger',
            'snapchat': 'com.snapchat.android',
            'tiktok': 'com.zhiliaoapp.musically',
            'netflix': 'com.netflix.mediaclient',
            'phonepe': 'com.phonepe.app',
            'gpay': 'com.google.android.apps.nbu.paisa.user',
            'paytm': 'net.one97.paytm'
        };

        // Request mic permission on load
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                stream.getTracks().forEach(t => t.stop());
                document.getElementById('status').innerText = 'Systems online. Ready!';
            })
            .catch(() => {
                document.getElementById('status').innerText = 'Please allow microphone!';
            });

        const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SR();
        recognition.lang = 'en-US';
        recognition.continuous = false;
        recognition.interimResults = false;

        let wakeActive = false;
        let wakeRec = null;
        let isListening = false;
        let history = [];
        let isSpeaking = false;

        function startListening() {
            if (isListening || isSpeaking) return;
            isListening = true;
            setRingState('listening');
            document.getElementById('status').innerText = '🎙️ Listening...';
            recognition.start();
        }

        recognition.onresult = function(e) {
            const text = e.results[0][0].transcript;
            document.getElementById('status').innerText = 'You: ' + text;
            setRingState('thinking');
            isListening = false;
            processCommand(text);
        }

        recognition.onerror = function(e) {
            document.getElementById('status').innerText = 'Error: ' + e.error;
            setRingState('');
            isListening = false;
        }

        recognition.onend = function() {
            isListening = false;
            if (!isSpeaking) setRingState('');
        }

        function setRingState(state) {
            const ring = document.getElementById('ring');
            ring.className = state ? state : '';
        }

        function processCommand(text) {
            const lower = text.toLowerCase();

            // Open app commands
            for (const [app, pkg] of Object.entries(appPackages)) {
                if (lower.includes('open ' + app) || lower.includes('launch ' + app) || lower.includes('start ' + app)) {
                    openApp(app, pkg);
                    return;
                }
            }

            // Call command
            if (lower.includes('call ')) {
                const name = text.replace(/call/i, '').trim();
                handleCall(name);
                return;
            }

            // SMS command
            if (lower.includes('send message') || lower.includes('send sms') || lower.includes('text ')) {
                handleSMS(text);
                return;
            }

            // Search command
            if (lower.includes('search for') || lower.includes('google ')) {
                const query = lower.replace('search for', '').replace('google', '').trim();
                handleSearch(query);
                return;
            }

            // YouTube search
            if (lower.includes('play ') || lower.includes('youtube ')) {
                const query = lower.replace('play', '').replace('youtube', '').trim();
                handleYouTube(query);
                return;
            }

            // Default - Ask AI
            askAI(text);
        }

        function openApp(appName, pkg) {
            const msg = 'Opening ' + appName + '!';
            showResult(msg);
            speak(msg);
            addHistory('ai', msg);

            // Try to open using intent URL
            const intentUrl = 'intent://#Intent;package=' + pkg + ';scheme=https;end';
            window.location.href = intentUrl;

            // Fallback to Play Store
            setTimeout(() => {
                window.location.href = 'market://details?id=' + pkg;
            }, 2000);
        }

        function handleCall(name) {
            const msg = 'Calling ' + name + ' now!';
            showResult(msg);
            speak(msg);
            addHistory('ai', msg);
            setTimeout(() => {
                window.location.href = 'tel:' + name.replace(/\s/g, '');
            }, 1500);
        }

        function handleSMS(text) {
            const msg = 'Opening messages!';
            showResult(msg);
            speak(msg);
            window.location.href = 'sms:';
        }

        function handleSearch(query) {
            const msg = 'Searching for ' + query;
            showResult(msg);
            speak(msg);
            setTimeout(() => {
                window.open('https://www.google.com/search?q=' + encodeURIComponent(query), '_blank');
            }, 1500);
        }

        function handleYouTube(query) {
            const msg = 'Playing ' + query + ' on YouTube!';
            showResult(msg);
            speak(msg);
            setTimeout(() => {
                window.open('https://www.youtube.com/results?search_query=' + encodeURIComponent(query), '_blank');
            }, 1500);
        }

        function sendCommand(cmd) {
            document.getElementById('status').innerText = 'You: ' + cmd;
            setRingState('thinking');
            processCommand(cmd);
        }

        function askAI(text) {
            addHistory('user', text);
            fetch('/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: text, history: history })
            })
            .then(r => r.json())
            .then(data => {
                showResult(data.answer);
                addHistory('ai', data.answer);
                speak(data.answer);
            })
            .catch(() => {
                showResult('Connection error! Check internet.');
                setRingState('');
            });
        }

        function showResult(text) {
            document.getElementById('result').innerText = text;
            setRingState('');
        }

        function speak(text) {
            window.speechSynthesis.cancel();
            const u = new SpeechSynthesisUtterance(text.substring(0, 200));
            u.lang = 'en-US';
            u.rate = 1.0;
            isSpeaking = true;
            setRingState('speaking');
            u.onend = () => {
                isSpeaking = false;
                setRingState('');
                document.getElementById('status').innerText = 'Ready! Tap or say Hey Jarvis';
                if (wakeActive) startWakeWord();
            };
            window.speechSynthesis.speak(u);
        }

        function toggleWake() {
            wakeActive = !wakeActive;
            const btn = document.getElementById('wakeBtn');
            if (wakeActive) {
                btn.className = 'active';
                btn.innerText = '((•)) Listening for Hey Jarvis...';
                startWakeWord();
                speak('Hey! Jarvis is now active and listening!');
            } else {
                btn.className = '';
                btn.innerText = '((•)) Say "Hey Jarvis"';
                if (wakeRec) wakeRec.stop();
            }
        }

        function startWakeWord() {
            if (!wakeActive) return;
            wakeRec = new SR();
            wakeRec.continuous = true;
            wakeRec.lang = 'en-US';
            wakeRec.onresult = function(e) {
                const text = e.results[e.results.length-1][0].transcript.toLowerCase();
                if (text.includes('hey jarvis') || text.includes('jarvis') || text.includes('hey buddy')) {
                    if (wakeRec) wakeRec.stop();
                    setTimeout(() => startListening(), 500);
                }
            }
            wakeRec.onend = function() {
                if (wakeActive && !isListening) {
                    setTimeout(() => startWakeWord(), 500);
                }
            }
            try { wakeRec.start(); } catch(e) {}
        }

        function addHistory(role, text) {
            history.push({role, text});
            if (history.length > 10) history.shift();
            const div = document.createElement('div');
            div.className = 'msg ' + role;
            div.innerText = (role === 'user' ? '👤 ' : '🤖 ') + text.substring(0, 80);
            const h = document.getElementById('history');
            h.insertBefore(div, h.firstChild);
            if (h.children.length > 6) h.removeChild(h.lastChild);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question', '')
    history = data.get('history', [])
    now = datetime.datetime.now().strftime("%I:%M %p, %B %d %Y")
    
    messages = [{
        "role": "system",
        "content": f"""You are JARVIS, an advanced AI assistant like Iron Man's JARVIS.
Current time: {now}
Be helpful, smart and concise. Max 50 words per answer.
For weather: use wttr.in
For calculations: solve directly
For jokes: tell funny ones
For news: give latest updates
Always be professional but friendly."""
    }]
    
    for h in history[-6:]:
        messages.append({
            "role": "user" if h['role'] == 'user' else "assistant",
            "content": h['text']
        })
    messages.append({"role": "user", "content": question})
    
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=messages,
        max_tokens=150
    )
    
    answer = response.choices[0].message.content
    return jsonify({"answer": answer})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
