from flask import Flask, render_template, request
from db import get_db_connection
from geo_lookup import get_country_from_ip
from utils.detector import (
    detect_attack_type,
    is_brute_force,
    BRUTE_FORCE_WINDOW_MINUTES,
)

app = Flask(__name__)


def get_client_ip(req):
    forwarded = req.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return req.remote_addr


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        ip = get_client_ip(request)
        country = get_country_from_ip(ip)
        user_agent = request.headers.get("User-Agent")
        path = request.path

        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*) as count FROM attacks
                WHERE ip_address = %s
                AND request_path = '/login'
                AND created_at >= NOW() - INTERVAL %s MINUTE
                """,
                (ip, BRUTE_FORCE_WINDOW_MINUTES),
            )
            result = cursor.fetchone()
            recent_attempts = result["count"]

            if is_brute_force(recent_attempts):
                attack_type = "brute_force"
                blocked = 1
            else:
                attack_type = "login_attempt"
                blocked = 0

            cursor.execute(
                """
                INSERT INTO attacks
                    (ip_address, country, request_path, method,
                     username_input, password_input, user_agent,
                     attack_type, is_blocked)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (ip, country, path, request.method, username, password,
                 user_agent, attack_type, blocked),
            )
        conn.commit()
        conn.close()
        return render_template("login_result.html")

    return render_template("login.html")


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        ip = get_client_ip(request)
        country = get_country_from_ip(ip)
        user_agent = request.headers.get("User-Agent")
        path = request.path

        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO attacks
                    (ip_address, country, request_path, method,
                     username_input, password_input, user_agent, attack_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (ip, country, path, request.method, username, password,
                 user_agent, "admin_probe"),
            )
        conn.commit()
        conn.close()
        return render_template("admin_result.html")

    return render_template("admin.html")


@app.route("/<path:subpath>", methods=["GET", "POST"])
def catch_all(subpath):
    full_path = "/" + subpath
    ip = get_client_ip(request)
    country = get_country_from_ip(ip)
    user_agent = request.headers.get("User-Agent")
    payload = request.query_string.decode("utf-8")
    attack_type = detect_attack_type(subpath)

    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO attacks
                (ip_address, country, request_path, method,
                 user_agent, payload, attack_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (ip, country, full_path, request.method,
             user_agent, payload, attack_type),
        )
    conn.commit()
    conn.close()
    return "404 Not Found", 404


@app.route("/dashboard")
def dashboard():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM attacks ORDER BY created_at DESC LIMIT 20")
        logs = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) as total FROM attacks")
        total = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) as brute FROM attacks WHERE attack_type = 'brute_force'")
        brute = cursor.fetchone()["brute"]

        cursor.execute("SELECT COUNT(*) as admin FROM attacks WHERE attack_type = 'admin_probe'")
        admin_count = cursor.fetchone()["admin"]

        cursor.execute("SELECT COUNT(DISTINCT ip_address) as unique_ips FROM attacks")
        unique_ips = cursor.fetchone()["unique_ips"]

        cursor.execute("SELECT COUNT(*) as suspicious FROM attacks WHERE attack_type = 'suspicious_path'")
        suspicious = cursor.fetchone()["suspicious"]

        cursor.execute(
            "SELECT COUNT(DISTINCT ip_address) as blocked_ips FROM attacks WHERE is_blocked = 1"
        )
        blocked_ips = cursor.fetchone()["blocked_ips"]

        cursor.execute(
            """
            SELECT ip_address, COUNT(*) as count
            FROM attacks
            GROUP BY ip_address
            ORDER BY count DESC
            LIMIT 5
            """
        )
        top_ips = cursor.fetchall()

        cursor.execute(
            """
            SELECT request_path, COUNT(*) as count
            FROM attacks
            GROUP BY request_path
            ORDER BY count DESC
            LIMIT 5
            """
        )
        top_paths = cursor.fetchall()

        cursor.execute(
            """
            SELECT attack_type, COUNT(*) as count
            FROM attacks
            GROUP BY attack_type
            ORDER BY count DESC
            """
        )
        attack_types = cursor.fetchall()

    conn.close()
    return render_template(
        "dashboard.html",
        logs=logs,
        total=total,
        brute=brute,
        admin=admin_count,
        unique_ips=unique_ips,
        top_ips=top_ips,
        top_paths=top_paths,
        attack_types=attack_types,
        suspicious=suspicious,
        blocked_ips=blocked_ips,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
