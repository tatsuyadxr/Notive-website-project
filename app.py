from flask import Flask, render_template_string, request, jsonify
import subprocess
import sys
import os

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
      background-blegit --version
gitnd-mode: overlay;
      color: #111827;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 40px;
    }
    .card{max-width:360px;margin:0 auto;background:#fff;padding:20px;border-radius:12px;box-shadow:0 6px 22px rgba(0,0,0,0.08)}
    label{display:block;margin-top:10px;color:#333}
    input,select,button{width:100%;padding:10px;border-radius:8px;border:1px solid #ddd;margin-top:8px;box-sizing:border-box}
    button.primary{background:#0aa1ff;color:#fff;border:none;margin-top:12px}
    .info{margin-top:14px;padding:12px;background:#0b1720;color:#fff;border-radius:10px;text-align:center}
  </style>
</head>
<body>
  <div class="card">
    <h3>Select game & answer</h3>

    <form id="userForm" method="POST" action="/">
      <label>Game</label>
      <select name="game" required>
        <option value="tictactoe" {% if submitted and game=='tictactoe' %}selected{% endif %}>Tic Tac Toe</option>
        <option value="snake" {% if submitted and game=='snake' %}selected{% endif %}>Snake</option>
        <option value="basic_calculator" {% if submitted and game=='basic_calculator' %}selected{% endif %}>Basic Calculator</option>
        <option value="scientific_calculator" {% if submitted and game=='scientific_calculator' %}selected{% endif %}>Scientific Calculator</option>
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

        <button id="launchBtn" class="primary" style="width:auto;margin-top:10px;" onclick="launchExternal()">Launch {{ game_label }}</button>
      </div>
    {% endif %}
  </div>

  <script>
    async function launchExternal(){
      try{
        // read values from the inputs (present only when submitted)
        const gameEl = document.getElementById('payload_game');
        const gameKeyEl = document.getElementById('payload_game_key');
        const nameEl = document.getElementById('payload_name');
        const ageEl = document.getElementById('payload_age');
        const countryEl = document.getElementById('payload_country');

        if(!gameEl){
          alert('No submission data found. Please submit the form first.');
          return;
        }

        const payload = {
          // use the hidden key for launching the correct script
          game: (gameKeyEl && gameKeyEl.value) ? gameKeyEl.value : (gameEl.value || 'tictactoe'),
          name: nameEl ? nameEl.value : '',
          age: ageEl ? ageEl.value : '',
          country: countryEl ? countryEl.value : ''
        };

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
      }catch(e){
        alert('Request failed: ' + e.message);
      }
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
        if game == "tictactoe":
          game_label = "Tic Tac Toe"
        elif game == "snake":
          game_label = "Snake"
        elif game == "basic_calculator":
          game_label = "Basic Calculator"
        elif game == "scientific_calculator":
          game_label = "Scientific Calculator"
        else:
          game_label = game

        return render_template_string(HTML_TEMPLATE,
                                      submitted=True,
                                      name=name,
                                      age=age,
                                      country=country,
                                      game=game,
                                      game_label=game_label)

    return render_template_string(HTML_TEMPLATE, submitted=False, name='', age='', country='', game='tictactoe')

@app.route("/launch", methods=["POST"])
def launch():
    """
    Launch the selected game script as a separate process on the machine
    running Flask. Expects JSON: { game, name, age, country }.
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
    }
    if game not in allowed:
      return jsonify({"ok": False, "error": "unsupported game"}), 400

    script_path = os.path.join(app.root_path, allowed[game])
    if not os.path.isfile(script_path):
        return jsonify({"ok": False, "error": f"script not found: {script_path}"}), 404

    try:
        # Build process args: pass name, age, country as argv
        args = [sys.executable, script_path, str(name or ""), str(age or ""), str(country or "")]

        # On Windows open in new console window
        popen_kwargs = {"cwd": app.root_path, "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
        if os.name == "nt":
          # Hide the console window on Windows when launching GUI games
          # CREATE_NO_WINDOW = 0x08000000
          popen_kwargs["creationflags"] = 0x08000000
        else:
          # recommended for POSIX when launching detached processes
          popen_kwargs["close_fds"] = True

        subprocess.Popen(args, **popen_kwargs)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

if __name__ == "__main__":
    # Run on localhost only (this launches processes on this machine).
    app.run(debug=True)
