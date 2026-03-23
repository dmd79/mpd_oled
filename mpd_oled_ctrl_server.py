#!/usr/bin/env python3
"""
mpd_oled control web server - port 8080
"""

import http.server
import socketserver
import json
import os
import threading
from urllib.parse import urlparse

PIPE_PATH = "/tmp/mpd_oled_ctrl"
STATE_PATH = "/home/pi/mpd_oled/state"
PORT = 8080

STATE_KEYS = [
    "spectrum_type", "full_spectrum", "bars_idx_64", "bars_idx_128",
    "sens_64_0", "sens_64_1", "sens_64_2",
    "sens_128_0", "sens_128_1", "sens_128_2",
    "sens_vu",
    "eq1", "eq2", "eq3", "eq4", "eq5"
]

DEFAULTS = {
    "spectrum_type": 0, "full_spectrum": 0,
    "bars_idx_64": 1, "bars_idx_128": 1,
    "sens_64_0": 50, "sens_64_1": 30, "sens_64_2": 20,
    "sens_128_0": 50, "sens_128_1": 30, "sens_128_2": 20,
    "sens_vu": 420,
    "eq1": 3.0, "eq2": 2.0, "eq3": 1.5, "eq4": 1.2, "eq5": 1.0,
}

BARS_64  = [6, 16, 21]
BARS_128 = [6, 16, 32]
SPECT_NAMES = ["Filled","Filled+Peaks","Dot","Inverted","Inv+Peaks",
               "VU Filled","VU+Peaks","VU Dot","VU Inv","VU Inv+Peaks"]
SCREEN_NAMES = ["Standard","Large","Full"]

state_lock = threading.Lock()

def read_state():
    state = DEFAULTS.copy()
    try:
        with open(STATE_PATH, "r") as f:
            parts = f.read().strip().split()
        for i, key in enumerate(STATE_KEYS):
            if i < len(parts):
                state[key] = float(parts[i]) if key.startswith("eq") else int(float(parts[i]))
    except Exception:
        pass
    return state

def write_state(state):
    line = " ".join(
        f"{state[k]:.2f}" if k.startswith("eq") else str(int(state[k]))
        for k in STATE_KEYS
    ) + "\n"
    with open(STATE_PATH, "w") as f:
        f.write(line)

def send_pipe(cmd):
    try:
        fd = os.open(PIPE_PATH, os.O_WRONLY | os.O_NONBLOCK)
        os.write(fd, (cmd + "\n").encode())
        os.close(fd)
        return True
    except Exception as e:
        print(f"Pipe error: {e}")
        return False

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>mpd_oled</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600&family=Syne:wght@700;800&display=swap" rel="stylesheet">
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --bg: #080810;
  --s1: #0f0f1a;
  --s2: #161625;
  --border: #2a2a45;
  --accent: #00e5ff;
  --accent2: #7c4dff;
  --text: #e0e0f0;
  --muted: #6060a0;
  --success: #00ff9d;
  --warn: #ffaa00;
  --danger: #ff4466;
}
body {
  background: var(--bg);
  color: var(--text);
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  min-height: 100vh;
  background-image:
    radial-gradient(ellipse at 20% 0%, rgba(0,229,255,0.04) 0%, transparent 60%),
    radial-gradient(ellipse at 80% 100%, rgba(124,77,255,0.04) 0%, transparent 60%);
}
header {
  padding: 20px 24px 14px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: baseline;
  gap: 16px;
}
header h1 { font-family:'Syne',sans-serif; font-size:20px; font-weight:800; color:var(--accent); }
header span { color:var(--muted); font-size:11px; }
#live-status {
  margin-left: auto;
  display: flex;
  gap: 16px;
  font-size: 11px;
  color: var(--muted);
}
#live-status b { color: var(--accent); font-weight:600; }
.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1px;
  background: var(--border);
  border-top: 1px solid var(--border);
}
@media (max-width: 700px) { .grid { grid-template-columns: 1fr; } }
.panel { background: var(--s1); padding: 18px 20px; }
.panel.full { grid-column: 1 / -1; }
.panel h2 {
  font-family:'Syne',sans-serif; font-size:10px; font-weight:700;
  text-transform:uppercase; letter-spacing:2px; color:var(--muted); margin-bottom:14px;
}
.row { display:flex; align-items:center; gap:10px; margin-bottom:10px; }
.row label { width:100px; color:var(--muted); font-size:11px; flex-shrink:0; }
.row input[type=range] {
  flex:1; -webkit-appearance:none; height:3px;
  background:var(--s2); border-radius:2px; outline:none; cursor:pointer;
}
.row input[type=range]::-webkit-slider-thumb {
  -webkit-appearance:none; width:13px; height:13px; border-radius:50%;
  background:var(--accent); cursor:pointer; box-shadow:0 0 7px var(--accent);
  transition:transform 0.1s;
}
.row input[type=range]::-webkit-slider-thumb:active { transform:scale(1.3); }
.row input[type=range].vu::-webkit-slider-thumb { background:var(--accent2); box-shadow:0 0 7px var(--accent2); }
.row input[type=range].eq::-webkit-slider-thumb { background:var(--warn); box-shadow:0 0 7px var(--warn); }
.val { width:42px; text-align:right; color:var(--accent); font-size:12px; font-weight:600; }
.val.vu { color:var(--accent2); }
.val.eq { color:var(--warn); }
.btn-row { display:flex; gap:6px; flex-wrap:wrap; margin-top:6px; }
button {
  background:var(--s2); border:1px solid var(--border); color:var(--text);
  font-family:'JetBrains Mono',monospace; font-size:11px;
  padding:6px 12px; cursor:pointer; border-radius:3px;
  transition:all 0.15s; letter-spacing:0.3px;
}
button:hover { border-color:var(--accent); color:var(--accent); }
button.active { background:rgba(0,229,255,0.12); border-color:var(--accent); color:var(--accent); }
button.apply { background:rgba(0,229,255,0.1); border-color:var(--accent); color:var(--accent); }
button.apply:hover { background:rgba(0,229,255,0.2); }
button.cmd { background:rgba(124,77,255,0.1); border-color:var(--accent2); color:var(--accent2); }
button.cmd:hover { background:rgba(124,77,255,0.2); }
button.danger { background:rgba(255,68,102,0.1); border-color:var(--danger); color:var(--danger); }
button.danger:hover { background:rgba(255,68,102,0.2); }
.seg-group { display:flex; gap:3px; flex-wrap:wrap; }
.seg {
  background:var(--s2); border:1px solid var(--border); color:var(--muted);
  font-family:'JetBrains Mono',monospace; font-size:10px;
  padding:5px 10px; cursor:pointer; border-radius:3px; transition:all 0.15s;
}
.seg:hover { border-color:var(--accent2); color:var(--accent2); }
.seg.active { background:rgba(124,77,255,0.15); border-color:var(--accent2); color:var(--text); }
#status {
  position:fixed; bottom:20px; right:20px;
  padding:8px 14px; border-radius:4px; font-size:11px;
  opacity:0; transition:opacity 0.3s; pointer-events:none;
}
#status.show { opacity:1; }
#status.ok { background:rgba(0,255,157,0.12); border:1px solid var(--success); color:var(--success); }
#status.err { background:rgba(255,68,102,0.12); border:1px solid var(--danger); color:var(--danger); }
.eq-visual {
  display:flex; gap:3px; align-items:flex-end; height:36px;
  margin-bottom:12px; padding:0 2px;
}
.eq-bar {
  flex:1; background:linear-gradient(to top, var(--warn), rgba(255,170,0,0.25));
  border-radius:2px 2px 0 0; transition:height 0.2s; min-height:2px;
}
</style>
</head>
<body>
<header>
  <h1>mpd_oled</h1>
  <span>control</span>
  <div id="live-status">
    <span>type <b id="st-type">—</b></span>
    <span>screen <b id="st-screen">—</b></span>
    <span>bars <b id="st-bars">—</b></span>
  </div>
</header>

<div class="grid">

  <!-- DISPLAY TYPE -->
  <div class="panel full">
    <h2>Spectrum Type</h2>
    <div class="seg-group" id="type-btns"></div>
  </div>

  <!-- SCREEN + BARS -->
  <div class="panel">
    <h2>Screen Layout</h2>
    <div class="seg-group" id="screen-btns"></div>
  </div>

  <div class="panel">
    <h2>Bars</h2>
    <div class="btn-row">
      <button class="cmd" onclick="pipeCmd('bars_down')">◀ Less</button>
      <button class="cmd" onclick="pipeCmd('bars_up')">More ▶</button>
    </div>
    <div class="btn-row" style="margin-top:10px">
      <button class="danger" onclick="pipeCmd('screensaver')">☾ Screensaver</button>
      <button onclick="pipeCmd('screensaver_off')">☀ Off</button>
    </div>
  </div>

  <!-- SENSITIVITY 64px -->
  <div class="panel">
    <h2>Sensitivity — 64px spectrum</h2>
    <div class="row">
      <label>6 bars</label>
      <input type="range" id="sens_64_0" min="1" max="500" oninput="updVal(this)">
      <span class="val" id="v_sens_64_0">—</span>
    </div>
    <div class="row">
      <label>16 bars</label>
      <input type="range" id="sens_64_1" min="1" max="500" oninput="updVal(this)">
      <span class="val" id="v_sens_64_1">—</span>
    </div>
    <div class="row">
      <label>21 bars</label>
      <input type="range" id="sens_64_2" min="1" max="500" oninput="updVal(this)">
      <span class="val" id="v_sens_64_2">—</span>
    </div>
    <div class="btn-row">
      <button class="apply" onclick="saveSens()">Save &amp; Apply</button>
    </div>
  </div>

  <!-- SENSITIVITY 128px -->
  <div class="panel">
    <h2>Sensitivity — 128px spectrum</h2>
    <div class="row">
      <label>6 bars</label>
      <input type="range" id="sens_128_0" min="1" max="500" oninput="updVal(this)">
      <span class="val" id="v_sens_128_0">—</span>
    </div>
    <div class="row">
      <label>16 bars</label>
      <input type="range" id="sens_128_1" min="1" max="500" oninput="updVal(this)">
      <span class="val" id="v_sens_128_1">—</span>
    </div>
    <div class="row">
      <label>32 bars</label>
      <input type="range" id="sens_128_2" min="1" max="500" oninput="updVal(this)">
      <span class="val" id="v_sens_128_2">—</span>
    </div>
    <div class="btn-row">
      <button class="apply" onclick="saveSens()">Save &amp; Apply</button>
    </div>
  </div>

  <!-- VU SENSITIVITY -->
  <div class="panel">
    <h2>Sensitivity — VU meter</h2>
    <div class="row">
      <label>Sensitivity</label>
      <input type="range" id="sens_vu" class="vu" min="1" max="1000" oninput="updVal(this)">
      <span class="val vu" id="v_sens_vu">—</span>
    </div>
    <div class="btn-row">
      <button class="apply" onclick="saveVu()">Save &amp; Apply</button>
    </div>
  </div>

  <!-- EQ -->
  <div class="panel full">
    <h2>Equalizer</h2>
    <div class="eq-visual">
      <div class="eq-bar" id="eqb1"></div>
      <div class="eq-bar" id="eqb2"></div>
      <div class="eq-bar" id="eqb3"></div>
      <div class="eq-bar" id="eqb4"></div>
      <div class="eq-bar" id="eqb5"></div>
    </div>
    <div class="row">
      <label>Band 1 bass</label>
      <input type="range" id="eq1" class="eq" min="1" max="10" step="0.1" oninput="updEq(this,1)">
      <span class="val eq" id="v_eq1">—</span>
    </div>
    <div class="row">
      <label>Band 2</label>
      <input type="range" id="eq2" class="eq" min="1" max="10" step="0.1" oninput="updEq(this,2)">
      <span class="val eq" id="v_eq2">—</span>
    </div>
    <div class="row">
      <label>Band 3 mid</label>
      <input type="range" id="eq3" class="eq" min="1" max="10" step="0.1" oninput="updEq(this,3)">
      <span class="val eq" id="v_eq3">—</span>
    </div>
    <div class="row">
      <label>Band 4</label>
      <input type="range" id="eq4" class="eq" min="1" max="10" step="0.1" oninput="updEq(this,4)">
      <span class="val eq" id="v_eq4">—</span>
    </div>
    <div class="row">
      <label>Band 5 treble</label>
      <input type="range" id="eq5" class="eq" min="1" max="10" step="0.1" oninput="updEq(this,5)">
      <span class="val eq" id="v_eq5">—</span>
    </div>
    <div class="btn-row" style="margin-top:8px">
      <button class="apply" onclick="saveEq()">Save &amp; Apply</button>
      <button onclick="resetEq()">Reset flat</button>
    </div>
  </div>

</div>
<div id="status"></div>

<script>
const TYPES  = ["Filled","Filled+Peaks","Dot","Inverted","Inv+Peaks",
                "VU Filled","VU+Peaks","VU Dot","VU Inv","VU Inv+Peaks"];
const SCREENS = ["Standard","Large","Full"];
let state = {};
let userEditing = false;
let editTimer = null;

// Mark user as editing — suppress poll updates for 5s after last interaction
function markEditing() {
  userEditing = true;
  clearTimeout(editTimer);
  editTimer = setTimeout(() => { userEditing = false; }, 5000);
}

// Build segment buttons
function buildSegs() {
  const tb = document.getElementById('type-btns');
  TYPES.forEach((n,i) => {
    const b = document.createElement('button');
    b.className = 'seg'; b.id = 'type_'+i; b.textContent = i+' '+n;
    b.onclick = () => setType(i);
    tb.appendChild(b);
  });
  const sb = document.getElementById('screen-btns');
  SCREENS.forEach((n,i) => {
    const b = document.createElement('button');
    b.className = 'seg'; b.id = 'screen_'+i; b.textContent = n;
    b.onclick = () => setScreen(i);
    sb.appendChild(b);
  });
}

function updVal(el) {
  markEditing();
  document.getElementById('v_'+el.id).textContent = el.value;
}
function updEq(el, n) {
  markEditing();
  document.getElementById('v_eq'+n).textContent = parseFloat(el.value).toFixed(1);
  document.getElementById('eqb'+n).style.height = ((el.value-1)/9*100)+'%';
}

async function loadState() {
  const r = await fetch('/state');
  state = await r.json();
  if (!userEditing) {
    ['sens_64_0','sens_64_1','sens_64_2',
     'sens_128_0','sens_128_1','sens_128_2','sens_vu'].forEach(k => {
      const el = document.getElementById(k);
      if (el) { el.value = state[k]; document.getElementById('v_'+k).textContent = state[k]; }
    });
    for (let i=1;i<=5;i++) {
      const el = document.getElementById('eq'+i);
      if (el) {
        el.value = state['eq'+i];
        document.getElementById('v_eq'+i).textContent = parseFloat(state['eq'+i]).toFixed(1);
        document.getElementById('eqb'+i).style.height = ((state['eq'+i]-1)/9*100)+'%';
      }
    }
  }
  updateLive();
}

function updateLive() {
  document.getElementById('st-type').textContent = TYPES[state.spectrum_type] || '—';
  document.getElementById('st-screen').textContent = SCREENS[state.full_spectrum] || '—';
  const isVu = state.spectrum_type >= 5;
  const w = state.full_spectrum === 0 ? 64 : 128;
  const presets = w===64 ? [6,16,21] : [6,16,32];
  const idx = w===64 ? state.bars_idx_64 : state.bars_idx_128;
  document.getElementById('st-bars').textContent = isVu ? '2 (VU)' : presets[idx];
  // highlight active type/screen
  TYPES.forEach((_,i) => {
    const b = document.getElementById('type_'+i);
    if (b) b.className = 'seg' + (i===state.spectrum_type ? ' active' : '');
  });
  SCREENS.forEach((_,i) => {
    const b = document.getElementById('screen_'+i);
    if (b) b.className = 'seg' + (i===state.full_spectrum ? ' active' : '');
  });
}

async function post(action, params) {
  const r = await fetch('/cmd', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({action, ...params})
  });
  const d = await r.json();
  showStatus(d.ok ? '✓ '+action : '✗ '+(d.error||'error'), d.ok);
  if (d.ok && d.state) { state = d.state; updateLive(); }
  return d.ok;
}

function pipeCmd(cmd) { post('pipe', {command: cmd}); }

function setType(i) {
  post('pipe', {command: 'set_type:' + i}).then(() => loadState());
}

function setScreen(i) {
  const diff = ((i - state.full_spectrum) + 3) % 3;
  const sends = diff === 1 ? ['next_screen'] : diff === 2 ? ['prev_screen'] : [];
  (async () => {
    for (const c of sends) await post('pipe', {command: c});
    await loadState();
  })();
}

function saveSens() {
  post('save_sens', {
    sens_64_0: +document.getElementById('sens_64_0').value,
    sens_64_1: +document.getElementById('sens_64_1').value,
    sens_64_2: +document.getElementById('sens_64_2').value,
    sens_128_0: +document.getElementById('sens_128_0').value,
    sens_128_1: +document.getElementById('sens_128_1').value,
    sens_128_2: +document.getElementById('sens_128_2').value,
  });
}

function saveVu() {
  post('sens_vu', {sens_vu: +document.getElementById('sens_vu').value});
}

function saveEq() {
  const eq = {};
  for (let i=1;i<=5;i++) eq['eq'+i] = +document.getElementById('eq'+i).value;
  post('eq', eq);
}

function resetEq() {
  for (let i=1;i<=5;i++) {
    document.getElementById('eq'+i).value = 1.0;
    document.getElementById('v_eq'+i).textContent = '1.0';
    document.getElementById('eqb'+i).style.height = '0%';
  }
  saveEq();
}

function showStatus(msg, ok) {
  const el = document.getElementById('status');
  el.textContent = msg; el.className = 'show '+(ok?'ok':'err');
  setTimeout(() => el.className='', 2500);
}

buildSegs();
loadState();
// Poll state every 3s to stay in sync with IR remote changes
setInterval(loadState, 3000);
</script>
</body>
</html>
"""

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass

    def do_GET(self):
        p = urlparse(self.path)
        if p.path == '/':
            self._respond(200, 'text/html', HTML.encode())
        elif p.path == '/state':
            with state_lock:
                s = read_state()
            self._respond(200, 'application/json', json.dumps(s).encode())
        else:
            self.send_response(404); self.end_headers()

    def do_POST(self):
        if self.path == '/cmd':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length))
            ok, err, new_state = self._handle(body)
            resp = {"ok": ok}
            if not ok: resp["error"] = err
            if new_state: resp["state"] = new_state
            self._respond(200, 'application/json', json.dumps(resp).encode())
        else:
            self.send_response(404); self.end_headers()

    def _respond(self, code, ct, data):
        self.send_response(code)
        self.send_header('Content-Type', ct)
        self.send_header('Content-Length', len(data))
        self.end_headers()
        self.wfile.write(data)

    def _handle(self, body):
        action = body.get('action')
        try:
            with state_lock:
                state = read_state()

            if action == 'pipe':
                ok = send_pipe(body['command'])
                return ok, None, None

            elif action == 'save_sens':
                for k in ['sens_64_0','sens_64_1','sens_64_2',
                          'sens_128_0','sens_128_1','sens_128_2']:
                    if k in body: state[k] = int(body[k])
                with state_lock:
                    write_state(state)
                send_pipe("sens_reload")
                return True, None, state

            elif action == 'sens_vu':
                state['sens_vu'] = int(body['sens_vu'])
                with state_lock:
                    write_state(state)
                send_pipe(f"sens_vu:{state['sens_vu']}")
                return True, None, state

            elif action == 'eq':
                for i in range(1, 6):
                    k = f'eq{i}'
                    if k in body: state[k] = float(body[k])
                with state_lock:
                    write_state(state)
                vals = ",".join(f"{state[f'eq{i}']:.2f}" for i in range(1, 6))
                send_pipe(f"eq:{vals}")
                return True, None, state

            return False, "unknown action", None
        except Exception as e:
            return False, str(e), None


if __name__ == '__main__':
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"mpd_oled control server on :{PORT}")
        httpd.serve_forever()
