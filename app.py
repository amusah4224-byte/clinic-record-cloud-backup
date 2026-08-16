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
        }

        .card {
            border: 1px solid #ddd;
            border-radius: 12px;
            padding: 20px;
        }

        button {
            padding: 12px 18px;
            margin: 8px 0;
            cursor: pointer;
        }

        li {
            margin: 10px 0;
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

    <form method="post" action="/backup">
        <button type="submit">
            Create Backup
        </button>
    </form>

    {% if message %}
        <p>
            <strong>{{ message }}</strong>
        </p>
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
