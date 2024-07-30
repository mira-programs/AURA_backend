CREATE DATABASE aura;

USE aura;

CREATE TABLE challenges (
    CHALLENGE_CODE INT,
    CHALLENGE_NAME VARCHAR(100),
    CHALLENGE_DATE DATE,
    CHALLENGE_DESC VARCHAR(1000),
    CHALLENGE_USER INT,
    --CHALLENGE_ACHIEVED CHAR(1)
);

CREATE TABLE account (
    ACCOUNT_ID INT PRIMARY KEY AUTO_INCREMENT,
    USERNAME VARCHAR(50) NOT NULL,
    EMAIL VARCHAR(100) NOT NULL,
    PASSWORD VARCHAR(255) NOT NULL,
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE achieved (
    
);