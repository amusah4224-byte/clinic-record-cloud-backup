from flask import Flask, render_template_string, redirect, url_for, request, send_file
import shutil
from datetime import datetime
from pathlib import Path
import os

app = Flask(__name__)

DATABASE = Path("clinic_records.db")
BACKUP_DIR = Path("backups")
BACKUP_DIR.mkdir(exist_ok=True)

PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Clinic Record Cloud Backup</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 30px auto;
            padding: 20px;
            background: #f5f7fa;
        }

        .card {
            background: white;
            border: 1px solid #ddd;
            border-radius: 12px;
            padding: 20px;
        }

        h1 {
            margin-bottom: 10px;
        }

        button {
            padding: 12px 18px;
            margin: 8px 0;
            cursor: pointer;
            border-radius: 6px;
            border: 1px solid #888;
            background: #f0f0f0;
        }

        select {
            padding: 10px;
            width: 100%;
            max-width: 500px;
            margin: 8px 0;
        }

        li {
            margin: 10px 0;
        }

        .message {
            margin-top: 15px;
            padding: 12px;
            background: #e8f5e9;
            border-radius: 6px;
        }

        .warning {
            margin-top: 15px;
            padding: 12px;
            background: #fff3cd;
            border-radius: 6px;
        }
    </style>
</head>

<body>

<div class="card">

    <h1>Clinic Record Cloud Backup</h1>

    <p>
        <strong>Database:</strong>
        {{ database }}
    </p>

    <!-- CREATE BACKUP -->

    <form method="post" action="/backup">
        <button type="submit">
            Create Backup
        </button>
    </form>

    {% if message %}
        <div class="message">
            <strong>{{ message }}</strong>
        </div>
    {% endif %}

    <h2>Available Backups</h2>

    {% if backups %}

        <ul>

        {% for backup in backups %}

            <li>
                <a href="/download/{{ backup }}">
                    {{ backup }}
                </a>
            </li>

        {% endfor %}

        </ul>

        <!-- RESTORE BACKUP -->

        <h2>Restore Database</h2>

        <div class="warning">
            <strong>Warning:</strong>
            Restoring a backup will replace the current clinic database.
        </div>

        <form method="post" action="/restore">

            <label for="backup">
                Select backup to restore:
            </label>

            <br>

            <select name="backup" id="backup" required>

                <option value="">
                    -- Select a backup --
                </option>

                {% for backup in backups %}

                    <option value="{{ backup }}">
                        {{ backup }}
                    </option>

                {% endfor %}

            </select>

            <br>

            <button type="submit"
                    onclick="return confirm('Are you sure you want to restore this backup? The current database will be replaced.');">

                Restore Selected Backup

            </button>

        </form>

    {% else %}

        <p>No backups created yet.</p>

    {% endif %}

</div>

</body>
</html>
"""


@app.route("/")
def home():

    backups = sorted(
        [p.name for p in BACKUP_DIR.glob("*.db")],
        reverse=True
    )

    return render_template_string(
        PAGE,
        database=DATABASE.name,
        backups=backups,
        message=request.args.get("message")
    )


@app.route("/backup", methods=["POST"])
def backup():

    if not DATABASE.exists():

        return redirect(
            url_for(
                "home",
                message="Database file clinic_records.db was not found."
            )
        )

    backup_name = (
        "clinic_backup_"
        + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        + ".db"
    )

    shutil.copy2(
        DATABASE,
        BACKUP_DIR / backup_name
    )

    return redirect(
        url_for(
            "home",
            message=f"Backup completed: {backup_name}"
        )
    )


@app.route("/download/<filename>")
def download(filename):

    path = BACKUP_DIR / filename

    if not path.exists() or path.suffix != ".db":

        return "Backup not found.", 404

    return send_file(
        path,
        as_attachment=True
    )


@app.route("/restore", methods=["POST"])
def restore():

    filename = request.form.get("backup")

    if not filename:

        return redirect(
            url_for(
                "home",
                message="Please select a backup to restore."
            )
        )

    backup_path = BACKUP_DIR / filename

    if not backup_path.exists() or backup_path.suffix != ".db":

        return redirect(
            url_for(
                "home",
                message="Selected backup was not found."
            )
        )

    try:

        shutil.copy2(
            backup_path,
            DATABASE
        )

        return redirect(
            url_for(
                "home",
                message=f"Database successfully restored from {filename}"
            )
        )

    except Exception as e:

        return redirect(
            url_for(
                "home",
                message=f"Restore failed: {str(e)}"
            )
        )


if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
