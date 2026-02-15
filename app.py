from flask import Flask, render_template_string, request, jsonify
import subprocess
import sys
import os
import time
from datetime import datetime

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>My first website</title>
  <link rel="icon" href="{{ url_for('static', filename='icon.png') }}" type="image/png">
  <style>
    body {
      margin: 0;
      min-height: 100vh;
      font-family: 'Poppins', 'Segoe UI', system-ui, -apple-system, Roboto, "Helvetica Neue", Arial;
      background-image: url("{{ url_for('static', filename='images.jpg') }}");
      background-position: center;
      background-size: cover;
      background-repeat: no-repeat;
      background-color: rgba(0,0,0,0.25);
      color: #111827;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 40px;
    }
    .card{max-width:520px;margin:0 auto;background:#fff;padding:20px;border-radius:12px;box-shadow:0 6px 22px rgba(0,0,0,0.08)}
    label{display:block;margin-top:10px;color:#333}
    input,select,button,textarea{width:100%;padding:10px;border-radius:8px;border:1px solid #ddd;margin-top:8px;box-sizing:border-box}
    button.primary{background:#0aa1ff;color:#fff;border:none;margin-top:12px}
    .info{margin-top:14px;padding:12px;background:#0b1720;color:#fff;border-radius:10px;text-align:center}
    .q-section{display:none;background:#f6f9fb;padding:10px;border-radius:8px;margin-top:8px}
    .inline{display:flex;gap:8px}
    .inline > * {flex:1}
  </style>
</head>
<body>
  <div class="card">
    <h3>Select game & answer</h3>

    <form id="userForm" method="POST" action="/">
      <label>Game</label>
      <select id="gameSelect" name="game" required onchange="onGameChange()">
        <option value="tictactoe" {% if submitted and game=='tictactoe' %}selected{% endif %}>Tic Tac Toe</option>
        <option value="snake" {% if submitted and game=='snake' %}selected{% endif %}>Snake</option>
        <option value="basic_calculator" {% if submitted and game=='basic_calculator' %}selected{% endif %}>Basic Calculator</option>
        <option value="scientific_calculator" {% if submitted and game=='scientific_calculator' %}selected{% endif %}>Scientific Calculator</option>
        <option value="planet3d" {% if submitted and game=='planet3d' %}selected{% endif %}>Planet 3D</option>
        <option value="qiskit_math" {% if submitted and game=='qiskit_math' %}selected{% endif %}>Qiskit Math</option>
      </select>

      <label>Your name</label>
      <input type="text" name="name" placeholder="Enter your name" required value="{{ name if submitted else '' }}">

      <label>Your age</label>
      <input type="number" name="age" placeholder="Enter your age" required value="{{ age if submitted else '' }}">

      <label>Country</label>
      <select name="country" required>
        <option value="">Select your country</option>
        {% for c in ['Malaysia','Japan','USA','Korea','Thailand'] %}
          <option {% if submitted and country==c %}selected{% endif %}>{{ c }}</option>
        {% endfor %}
      </select>

      <!-- Qiskit math extra fields (shown only when Qiskit Math is selected) -->
      <div id="qiskitSection" class="q-section">
        <label>Operation</label>
        <select name="q_op" id="q_op" onchange="onQOpChange()">
          <option value="fidelity" {% if submitted and q_op=='fidelity' %}selected{% endif %}>Fidelity (between two states)</option>
          <option value="bloch" {% if submitted and q_op=='bloch' %}selected{% endif %}>Bloch vector (single qubit)</option>
          <option value="expectation" {% if submitted and q_op=='expectation' %}selected{% endif %}>Expectation value (Pauli string)</option>
          <option value="inner" {% if submitted and q_op=='inner' %}selected{% endif %}>Inner product (&lt;ψ|φ&gt;)</option>
          <option value="qft" {% if submitted and q_op=='qft' %}selected{% endif %}>Apply QFT (statevector)</option>
        </select>

        <div style="margin-top:8px">
          <label>State 1 input method</label>
          <select name="q_state1_type" id="q_state1_type" onchange="onStateTypeChange(1)">
            <option value="predefined" {% if submitted and q_state1_type=='predefined' %}selected{% endif %}>Predefined (|0>,|1>,|+>,|-)</option>
            <option value="raw" {% if submitted and q_state1_type=='raw' %}selected{% endif %}>Raw amplitudes (comma separated)</option>
          </select>

          <div id="q_state1_predef" style="margin-top:6px;">
            <select name="q_state1_pre" id="q_state1_pre">
              <option value="0" {% if submitted and q_state1_pre=='0' %}selected{% endif %}>|0></option>
              <option value="1" {% if submitted and q_state1_pre=='1' %}selected{% endif %}>|1></option>
              <option value="+" {% if submitted and q_state1_pre=='+' %}selected{% endif %}>|+></option>
              <option value="-" {% if submitted and q_state1_pre=='-' %}selected{% endif %}>|-></option>
            </select>
          </div>

          <div id="q_state1_raw" style="margin-top:6px;display:none;">
            <input name="q_state1_raw_val" id="q_state1_raw_val" placeholder="e.g. 1,0  or  0.707+0.707j,0.707-0.707j" value="{{ q_state1_raw_val if submitted else '' }}">
          </div>
        </div>

        <!-- State 2 (shown for fidelity/inner) -->
        <div id="state2Block" style="margin-top:8px;display:none;">
          <label>State 2 input method</label>
          <select name="q_state2_type" id="q_state2_type" onchange="onStateTypeChange(2)">
            <option value="predefined" {% if submitted and q_state2_type=='predefined' %}selected{% endif %}>Predefined</option>
            <option value="raw" {% if submitted and q_state2_type=='raw' %}selected{% endif %}>Raw amplitudes</option>
          </select>

          <div id="q_state2_predef" style="margin-top:6px;">
            <select name="q_state2_pre" id="q_state2_pre">
              <option value="0" {% if submitted and q_state2_pre=='0' %}selected{% endif %}>|0></option>
              <option value="1" {% if submitted and q_state2_pre=='1' %}selected{% endif %}>|1></option>
              <option value="+" {% if submitted and q_state2_pre=='+' %}selected{% endif %}>|+></option>
              <option value="-" {% if submitted and q_state2_pre=='-' %}selected{% endif %}>|-></option>
            </select>
          </div>

          <div id="q_state2_raw" style="margin-top:6px;display:none;">
            <input name="q_state2_raw_val" id="q_state2_raw_val" placeholder="e.g. 0,1  or  0.6+0.8j,0" value="{{ q_state2_raw_val if submitted else '' }}">
          </div>
        </div>

        <div id="pauliBlock" style="margin-top:8px;display:none;">
          <label>Pauli string (for expectation)</label>
          <input name="q_pauli" id="q_pauli" placeholder="e.g. Z or ZI or IXX" value="{{ q_pauli if submitted else 'Z' }}">
        </div>

        <div id="qftBlock" style="margin-top:8px;display:none;">
          <label>Number of qubits (for QFT)</label>
          <input type="number" min="1" max="6" name="q_nqubits" id="q_nqubits" placeholder="e.g. 2" value="{{ q_nqubits if submitted else 2 }}">
          <label style="margin-top:6px">Statevector (optional; leave empty to use |0...0&gt;)</label>
          <input name="q_state_raw_for_qft" id="q_state_raw_for_qft" placeholder="comma-separated amplitudes" value="{{ q_state_raw_for_qft if submitted else '' }}">
        </div>

        <div style="margin-top:8px">
          <label>Save qiskit result to file (optional)</label>
          <input name="q_outfile" id="q_outfile" placeholder="e.g. static/q_result.json" value="{{ q_outfile if submitted else '' }}">
        </div>
      </div>

      <!-- Planet3D extra fields (shown only when Planet 3D is selected) -->
      <div id="planet3dSection" class="q-section">
        <label>Planet type</label>
        <div class="inline">
          <select name="planet_type" id="planet_type" onchange="onPlanetChange()">
            <option value="earth" {% if submitted and planet_type=='earth' %}selected{% endif %}>Earth</option>
            <option value="mars" {% if submitted and planet_type=='mars' %}selected{% endif %}>Mars</option>
            <option value="jupiter" {% if submitted and planet_type=='jupiter' %}selected{% endif %}>Jupiter</option>
            <option value="venus" {% if submitted and planet_type=='venus' %}selected{% endif %}>Venus</option>
            <option value="moon" {% if submitted and planet_type=='moon' %}selected{% endif %}>Moon</option>
          </select>

          <div style="width:140px;margin-left:8px;">
            <img id="planetPreview" alt="planet preview" style="width:100%;height:100px;object-fit:cover;border-radius:8px;border:1px solid #ddd;" src="{{ url_for('static', filename=('planet_' ~ (planet_type if submitted else 'earth') ~ '.png')) }}">
          </div>
        </div>

        <div id="planetGallery" style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap;">
          {% for p in ['earth','mars','jupiter','venus','moon'] %}
            <img class="thumb" data-planet="{{ p }}" title="{{ p }}" src="{{ url_for('static', filename=('planet_' ~ p ~ '.png')) }}" style="width:64px;height:64px;object-fit:cover;border-radius:8px;border:1px solid #ddd;cursor:pointer" onclick="selectPlanetFromThumb('{{ p }}')">
          {% endfor %}
        </div>

        <label style="margin-top:8px">Rotation (degrees)</label>
        <input type="number" name="planet_rotation" id="planet_rotation" min="0" max="360" step="1" value="{{ planet_rotation if submitted else 0 }}">

        <div style="margin-top:8px" class="inline">
          <label style="width:auto">Save figure to static</label>
          <select name="planet_save" id="planet_save">
            <option value="off" {% if submitted and planet_save!='on' %}selected{% endif %}>No</option>
            <option value="on" {% if submitted and planet_save=='on' %}selected{% endif %}>Yes</option>
          </select>
        </div>

        <label style="margin-top:8px">Output filename (optional)</label>
        <input name="planet_outfile" id="planet_outfile" placeholder="e.g. myplanet.png (saved to /static)" value="{{ planet_outfile if submitted else '' }}">
      </div>

      <button class="primary" type="submit">Submit</button>
    </form>

    {% if submitted %}
      <div class="info" id="submittedInfo">
        Hello <b>{{ name }}</b> — {{ age }} years • {{ country }}<br>

        <!-- show selected game in a visible textbox (readonly) so you can confirm/edit before launch -->
        <label style="margin-top:8px;color:#fff">Selected game</label>
        <input id="payload_game" type="text" value="{{ game_label }}" readonly>
        <!-- hidden input keeps the actual game key (used when launching) -->
        <input type="hidden" id="payload_game_key" value="{{ game }}">

        <!-- keep the other values in visible (or hidden) inputs so JS can send them reliably -->
        <input type="hidden" id="payload_name" value="{{ name|e }}">
        <input type="hidden" id="payload_age" value="{{ age }}">
        <input type="hidden" id="payload_country" value="{{ country|e }}">

        <!-- qiskit payloads (only populated when game == qiskit_math) -->
        <input type="hidden" id="payload_q_op" value="{{ q_op if submitted else '' }}">
        <input type="hidden" id="payload_q_state1_type" value="{{ q_state1_type if submitted else 'predefined' }}">
        <input type="hidden" id="payload_q_state1_pre" value="{{ q_state1_pre if submitted else '0' }}">
        <input type="hidden" id="payload_q_state1_raw_val" value="{{ q_state1_raw_val if submitted else '' }}">
        <input type="hidden" id="payload_q_state2_type" value="{{ q_state2_type if submitted else 'predefined' }}">
        <input type="hidden" id="payload_q_state2_pre" value="{{ q_state2_pre if submitted else '0' }}">
        <input type="hidden" id="payload_q_state2_raw_val" value="{{ q_state2_raw_val if submitted else '' }}">
        <input type="hidden" id="payload_q_pauli" value="{{ q_pauli if submitted else '' }}">
        <input type="hidden" id="payload_q_nqubits" value="{{ q_nqubits if submitted else '' }}">
        <input type="hidden" id="payload_q_state_raw_for_qft" value="{{ q_state_raw_for_qft if submitted else '' }}">
        <input type="hidden" id="payload_q_outfile" value="{{ q_outfile if submitted else '' }}">

        <!-- planet3d payloads (only populated when game == planet3d) -->
        <input type="hidden" id="payload_planet_type" value="{{ planet_type if submitted else 'earth' }}">
        <input type="hidden" id="payload_planet_rotation" value="{{ planet_rotation if submitted else 0 }}">
        <input type="hidden" id="payload_planet_save" value="{{ planet_save if submitted else 'off' }}">
        <input type="hidden" id="payload_planet_outfile" value="{{ planet_outfile if submitted else '' }}">

        <button id="launchBtn" class="primary" style="width:auto;margin-top:10px;" onclick="launchExternal()">Launch {{ game_label }}</button>
      </div>
    {% endif %}
  </div>

  <script>
    function onGameChange(){
      const sel = document.getElementById('gameSelect').value;
      document.getElementById('qiskitSection').style.display = (sel === 'qiskit_math') ? 'block' : 'none';
      document.getElementById('planet3dSection').style.display = (sel === 'planet3d') ? 'block' : 'none';
    }
    function onQOpChange(){
      const op = document.getElementById('q_op').value;
      document.getElementById('state2Block').style.display = (op === 'fidelity' || op === 'inner') ? 'block' : 'none';
      document.getElementById('pauliBlock').style.display = (op === 'expectation') ? 'block' : 'none';
      document.getElementById('qftBlock').style.display = (op === 'qft') ? 'block' : 'none';
    }
    function onStateTypeChange(idx){
      const type = document.getElementById('q_state'+idx+'_type').value;
      document.getElementById('q_state'+idx+'_predef').style.display = (type === 'predefined') ? 'block' : 'none';
      document.getElementById('q_state'+idx+'_raw').style.display = (type === 'raw') ? 'block' : 'none';
    }

    // Planet preview helpers
    function onPlanetChange(){
      const sel = document.getElementById('planet_type');
      const planet = sel ? sel.value : 'earth';
      const preview = document.getElementById('planetPreview');
      if(preview) preview.src = '/static/planet_' + planet + '.png';
      // highlight selected thumb
      document.querySelectorAll('.thumb').forEach(t => t.style.boxShadow = (t.dataset.planet === planet) ? '0 0 0 3px rgba(10,161,255,0.15)' : '');
    }
    function selectPlanetFromThumb(p){
      const sel = document.getElementById('planet_type');
      if(sel) sel.value = p; onPlanetChange();
    }

    // initialize visibility based on server-rendered values
    try{ onGameChange(); onQOpChange(); onStateTypeChange(1); onStateTypeChange(2); onPlanetChange(); }catch(e){}

    async function launchExternal(){
      try{
        const gameEl = document.getElementById('payload_game');
        const gameKeyEl = document.getElementById('payload_game_key');
        const nameEl = document.getElementById('payload_name');
        const ageEl = document.getElementById('payload_age');
        const countryEl = document.getElementById('payload_country');

        if(!gameEl){ alert('No submission data found. Please submit the form first.'); return; }

        const payload = {
          game: (gameKeyEl && gameKeyEl.value) ? gameKeyEl.value : (gameEl.value || 'tictactoe'),
          name: nameEl ? nameEl.value : '',
          age: ageEl ? ageEl.value : '',
          country: countryEl ? countryEl.value : ''
        };

        // qiskit-specific fields (if present)
        const qop = document.getElementById('payload_q_op');
        if(qop && qop.value){
          payload.q_op = qop.value;
          payload.q_state1_type = document.getElementById('payload_q_state1_type').value;
          payload.q_state1_pre = document.getElementById('payload_q_state1_pre').value;
          payload.q_state1_raw_val = document.getElementById('payload_q_state1_raw_val').value;
          payload.q_state2_type = document.getElementById('payload_q_state2_type').value;
          payload.q_state2_pre = document.getElementById('payload_q_state2_pre').value;
          payload.q_state2_raw_val = document.getElementById('payload_q_state2_raw_val').value;
          payload.q_pauli = document.getElementById('payload_q_pauli').value;
          payload.q_nqubits = document.getElementById('payload_q_nqubits').value;
          payload.q_state_raw_for_qft = document.getElementById('payload_q_state_raw_for_qft').value;
          payload.q_outfile = document.getElementById('q_outfile') ? document.getElementById('q_outfile').value : '';
        }

        // planet3d-specific fields (if present)
        const ptype = document.getElementById('payload_planet_type');
        if(ptype && ptype.value){
          payload.planet_type = ptype.value;
          payload.planet_rotation = document.getElementById('payload_planet_rotation').value;
          payload.planet_save = document.getElementById('payload_planet_save').value;
          payload.planet_outfile = document.getElementById('payload_planet_outfile').value;
        }

        const res = await fetch('/launch', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const body = await res.json();
        if(body.ok){
          const label = gameEl ? gameEl.value : payload.game;
          alert(label + ' launched (check your desktop).');
        } else {
          alert('Launch failed: ' + (body.error || 'unknown'));
        }
      }catch(e){ alert('Request failed: ' + e.message); }
    }
  </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        game = request.form.get("game", "tictactoe")
        name = request.form.get("name", "")
        age = request.form.get("age", "")
        country = request.form.get("country", "")

        # collect qiskit-specific form fields when qiskit option is used
        q_op = request.form.get("q_op", "")
        q_state1_type = request.form.get("q_state1_type", "predefined")
        q_state1_pre = request.form.get("q_state1_pre", "0")
        q_state1_raw_val = request.form.get("q_state1_raw_val", "")
        q_state2_type = request.form.get("q_state2_type", "predefined")
        q_state2_pre = request.form.get("q_state2_pre", "0")
        q_state2_raw_val = request.form.get("q_state2_raw_val", "")
        q_pauli = request.form.get("q_pauli", "Z")
        q_nqubits = request.form.get("q_nqubits", "2")
        q_state_raw_for_qft = request.form.get("q_state_raw_for_qft", "")
        q_outfile = request.form.get("q_outfile", "")

        # collect planet3d-specific form fields when planet3d option is used
        planet_type = request.form.get("planet_type", "earth")
        planet_rotation = request.form.get("planet_rotation", "0")
        planet_save = request.form.get("planet_save", "off")
        planet_outfile = request.form.get("planet_outfile", "")
        if game == "tictactoe":
          game_label = "Tic Tac Toe"
        elif game == "snake":
          game_label = "Snake"
        elif game == "basic_calculator":
          game_label = "Basic Calculator"
        elif game == "scientific_calculator":
          game_label = "Scientific Calculator"
        elif game == "qiskit_math":
          game_label = "Qiskit Math"
        elif game == "planet3d":
          game_label = "Planet 3D"
        else:
          game_label = game

        return render_template_string(HTML_TEMPLATE,
                                      submitted=True,
                                      name=name,
                                      age=age,
                                      country=country,
                                      game=game,
                                      game_label=game_label,
                                      q_op=q_op,
                                      q_state1_type=q_state1_type,
                                      q_state1_pre=q_state1_pre,
                                      q_state1_raw_val=q_state1_raw_val,
                                      q_state2_type=q_state2_type,
                                      q_state2_pre=q_state2_pre,
                                      q_state2_raw_val=q_state2_raw_val,
                                      q_pauli=q_pauli,
                                      q_nqubits=q_nqubits,
                                      q_state_raw_for_qft=q_state_raw_for_qft,
                                      planet_type=planet_type,
                                      planet_rotation=planet_rotation,
                                      planet_save=planet_save,
                                      planet_outfile=planet_outfile)
    return render_template_string(HTML_TEMPLATE, submitted=False, name='', age='', country='', game='tictactoe')

@app.route("/launch", methods=["POST"])
def launch():
    """
    Launch the selected script or run a qiskit math command as a separate
    background process. Expects JSON with game and optional qiskit fields.
    """
    data = request.get_json(silent=True) or {}
    game = data.get("game", "tictactoe")
    name = data.get("name", "")
    age = data.get("age", "")
    country = data.get("country", "")

    # allow specific scripts (map logical name -> filename)
    allowed = {
      "tictactoe": "tictactoe.py",
      "snake": "snake.py",
      "basic_calculator": "calculator.py",
      "scientific_calculator": "calculator_scientific.py",
      "qiskit_math": "qiskitquantum.py",
      "planet3d": "planet3d.py",
    }
    if game not in allowed:
      return jsonify({"ok": False, "error": "unsupported game"}), 400

    script_path = os.path.join(app.root_path, allowed[game])
    if not os.path.isfile(script_path):
        return jsonify({"ok": False, "error": f"script not found: {script_path}"}), 404

    try:
        # If launching qiskit_math, build CLI args from q_* payload fields
        if game == "qiskit_math":
            q_op = data.get("q_op", "fidelity")
            args = [sys.executable, script_path, "--cmd", q_op]

            # helper to read state (predefined vs raw)
            def state_arg(prefix):
                t = data.get(f"{prefix}_type", "predefined")
                if t == "predefined":
                    return data.get(f"{prefix}_pre", "0")
                return data.get(f"{prefix}_raw_val", "")

            if q_op in ("fidelity", "inner"):
                s1 = state_arg('q_state1')
                s2 = state_arg('q_state2')
                args += ["--state1", s1, "--state2", s2]
            elif q_op == "bloch":
                s1 = state_arg('q_state1')
                args += ["--state", s1]
            elif q_op == "expectation":
                s1 = state_arg('q_state1')
                pauli = data.get('q_pauli', 'Z')
                args += ["--state", s1, "--pauli", pauli]
            elif q_op == "qft":
                n = int(data.get('q_nqubits') or 1)
                args += ["--nqubits", str(n)]
                raw = data.get('q_state_raw_for_qft', '')
                if raw:
                    args += ["--state", raw]

            # optional outfile for qiskit CLI
            q_out = data.get('q_outfile', '').strip()
            if q_out:
                args += ["--out-file", q_out]
                expected_out = q_out
            else:
                expected_out = None

            # keep name/age/country as context if needed
            args += [str(name or ""), str(age or ""), str(country or "")]
        elif game == "planet3d":
            # Launch planet3d.py with NO CLI arguments — let the script run its builtin demo/defaults.
            # This intentionally ignores the planet3d form fields and starts the script without flags.
            args = [sys.executable, script_path]
        else:
            # Build process args for normal scripts: pass name, age, country as argv
            args = [sys.executable, script_path, str(name or ""), str(age or ""), str(country or "")]

        # On Windows open in new console window; run detached (background)
        popen_kwargs = {"cwd": app.root_path, "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
        if os.name == "nt":
          popen_kwargs["creationflags"] = 0x08000000
        else:
          popen_kwargs["close_fds"] = True

        # write debug log of the exact command we will run
        try:
            with open(os.path.join(app.root_path, 'launch_debug.log'), 'a', encoding='utf-8') as lf:
                lf.write(f"{datetime.utcnow().isoformat()} - launching: {args}\n")
        except Exception:
            pass

        proc = subprocess.Popen(args, **popen_kwargs)

        # if we know an expected output file, poll briefly for its creation so the UI can link to it
        saved = None
        expected = None
        # planet3d sets outp variable earlier when save_flag == 'on'
        if locals().get('outp'):
            expected = locals().get('outp')
        # qiskit may set expected_out above
        if locals().get('expected_out'):
            expected = locals().get('expected_out')

        if expected:
            abs_expected = expected if os.path.isabs(expected) else os.path.join(app.root_path, expected)
            for _ in range(30):
                if os.path.exists(abs_expected):
                    saved = expected
                    break
                time.sleep(0.1)

        # log pid
        try:
            with open(os.path.join(app.root_path, 'launch_debug.log'), 'a', encoding='utf-8') as lf:
                lf.write(f"{datetime.utcnow().isoformat()} - pid: {proc.pid} - expected_out: {expected}\n")
        except Exception:
            pass

        resp = {"ok": True}
        if saved:
            resp['saved'] = saved
        return jsonify(resp)
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

if __name__ == "__main__":
    # Run on localhost only (this launches processes on this machine).
    app.run(debug=True)
