CREATE DATABASE IF NOT EXISTS honeypot_db;
USE honeypot_db;

CREATE TABLE IF NOT EXISTS attacks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ip_address VARCHAR(45),
    country VARCHAR(100),
    request_path VARCHAR(255),
    method VARCHAR(10),
    username_input VARCHAR(255),
    password_input VARCHAR(255),
    user_agent TEXT,
    payload TEXT,
    attack_type VARCHAR(50),
    is_blocked TINYINT(1) DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
