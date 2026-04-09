SUSPICIOUS_PATHS = [
    "phpmyadmin",
    ".env",
    "wp-login.php",
    "admin.php",
    "config.php",
    ".git",
    "backup",
    "login.php",
]

BRUTE_FORCE_THRESHOLD = 5
BRUTE_FORCE_WINDOW_MINUTES = 5


def detect_attack_type(subpath):
    """Classify a catch-all path hit as suspicious or unknown."""
    for item in SUSPICIOUS_PATHS:
        if item in subpath.lower():
            return "suspicious_path"
    return "unknown_probe"


def is_brute_force(recent_attempts):
    """Return True if recent login attempts exceed the threshold."""
    return recent_attempts >= BRUTE_FORCE_THRESHOLD
