CREATE DATABASE aura;

USE aura;

CREATE TABLE challenges (
    id INT PRIMARY KEY AUTO_INCREMENT,
    description VARCHAR(1000),
    points INT
);

CREATE TABLE accounts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,  
    points INT DEFAULT 0,
    first_name VARCHAR(100),
    last_name VARCHAR(100)
);

CREATE TABLE completed_challenges (
    account_id INT,
    challenge_id INT,
    PRIMARY KEY(account_id, challenge_id),
    FOREIGN KEY(account_id) REFERENCES accounts(id),
    FOREIGN KEY(challenge_id) REFERENCES challenges(id)
);

CREATE TABLE friends (
    account_id INT,
    friend_id INT,
    PRIMARY KEY(account_id, friend_id),
    FOREIGN KEY(account_id) REFERENCES accounts(id),
    FOREIGN KEY(friend_id) REFERENCES accounts(id)
);
