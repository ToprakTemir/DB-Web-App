DROP DATABASE IF EXISTS ChessDB;
CREATE DATABASE IF NOT EXISTS ChessDB;
USE ChessDB;

CREATE TABLE DBManagers(
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(50) NOT NULL
);

CREATE TABLE Titles(
    title_ID INT PRIMARY KEY,
    title_name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE Players(
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(50) NOT NULL,
    name VARCHAR(50) NOT NULL,
    surname VARCHAR(50) NOT NULL,
    nationality VARCHAR(50) NOT NULL,
    date_of_birth DATE NOT NULL,
    fide_ID VARCHAR(7) NOT NULL, # FIDEXXX
    elo_rating INT NOT NULL,
    title_id INT NOT NULL,
    FOREIGN KEY (title_id) REFERENCES Titles(title_id)
                                ON DELETE RESTRICT
                                ON UPDATE CASCADE,
    CHECK (elo_rating >= 1000)
);

CREATE TABLE Sponsors(
    sponsor_id INT PRIMARY KEY,
    sponsor_name VARCHAR(50) NOT NULL
);

CREATE TABLE Teams(
    team_id INT PRIMARY KEY,
    team_name VARCHAR(50) NOT NULL,
    sponsor_id INT NOT NULL,
    FOREIGN KEY (sponsor_id) REFERENCES Sponsors(sponsor_id)
                                    ON DELETE RESTRICT
                                    ON UPDATE CASCADE
);

CREATE TABLE PlayerTeams(
    username VARCHAR(50),
    team_id INT NOT NULL,
    PRIMARY KEY (username, team_id), # Multiple teams allowed for players
    FOREIGN KEY (username) REFERENCES Players(username)
                                ON DELETE CASCADE
                                ON UPDATE CASCADE,
    FOREIGN KEY (team_id) REFERENCES Teams(team_id)
                                ON DELETE CASCADE
                                ON UPDATE CASCADE
);

CREATE TABLE Coaches(
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(50) NOT NULL,
    name VARCHAR(50) NOT NULL,
    surname VARCHAR(50) NOT NULL,
    nationality VARCHAR(50) NOT NULL,
    team_id INT NOT NULL,
    contract_start DATE NOT NULL,
    contract_finish DATE NOT NULL,
    UNIQUE (username, contract_start),  # Multiple contract records allowed for coaches
    FOREIGN KEY (team_id) REFERENCES Teams(team_id)
                                ON DELETE CASCADE
                                ON UPDATE CASCADE
);

CREATE TABLE CoachCertifications(
      coach_username VARCHAR(50) NOT NULL,
      certification VARCHAR(50) NOT NULL, 
      PRIMARY KEY (coach_username, certification),
      FOREIGN KEY (coach_username) REFERENCES Coaches(username)
                                    ON DELETE CASCADE
                                    ON UPDATE CASCADE
);

CREATE TABLE Arbiters(
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(50) NOT NULL,
    name VARCHAR(50) NOT NULL,
    surname VARCHAR(50) NOT NULL,
    nationality VARCHAR(50) NOT NULL,

    experience_level VARCHAR(50) NOT NULL
);

CREATE TABLE ArbiterCertifications(
    username VARCHAR(50) NOT NULL,
    certification VARCHAR(50) NOT NULL,
    PRIMARY KEY (username, certification),
    FOREIGN KEY (username) REFERENCES Arbiters(username)
                              ON DELETE CASCADE
                              ON UPDATE CASCADE
);

CREATE TABLE Halls(
      hall_id INT PRIMARY KEY,
      hall_name VARCHAR(50) NOT NULL,
      country VARCHAR(50) NOT NULL,
      capacity INT NOT NULL,

      UNIQUE (hall_name)
);


CREATE TABLE Tables(
       table_id INT PRIMARY KEY,
       hall_id INT NOT NULL,

       FOREIGN KEY (hall_id) REFERENCES Halls(hall_id)
           ON DELETE CASCADE
           ON UPDATE CASCADE
);

CREATE TABLE Matches(
    match_id INT PRIMARY KEY,
    date DATE NOT NULL,
    time_slot ENUM('1', '2', '3', '4') NOT NULL,
    hall_id INT NOT NULL,
    table_id INT NOT NULL,
    team1_id INT NOT NULL,
    team2_id INT NOT NULL,
    arbiter_username VARCHAR(50) NOT NULL,
    ratings FLOAT,

    UNIQUE (date, time_slot, table_ID), # makes sure that there is only one match in a table at a given time slot
    UNIQUE (date, time_slot, arbiter_username), # makes sure that an arbiter oversees only one match at any given time
    
    FOREIGN KEY (hall_id) REFERENCES Halls(hall_id)
                                    ON DELETE RESTRICT
                                    ON UPDATE CASCADE,
    FOREIGN KEY (table_id) REFERENCES Tables(table_id)
                                    ON DELETE RESTRICT
                                    ON UPDATE CASCADE,
    FOREIGN KEY (team1_id) REFERENCES Teams(team_id)
                                    ON DELETE RESTRICT
                                    ON UPDATE CASCADE,
    FOREIGN KEY (team2_id) REFERENCES Teams(team_id)
                                    ON DELETE RESTRICT
                                    ON UPDATE CASCADE,
    FOREIGN KEY (arbiter_username) REFERENCES Arbiters(username)
                                    ON DELETE RESTRICT
                                    ON UPDATE CASCADE
);

CREATE TABLE MatchAssignments(
    match_id INT PRIMARY KEY,
    white_player VARCHAR(50),
    black_player VARCHAR(50),
    team1_id INT NOT NULL,
    team2_id INT NOT NULL,
    result VARCHAR(50),
    FOREIGN KEY (match_id) REFERENCES Matches(match_id)
                                    ON DELETE RESTRICT
                                    ON UPDATE CASCADE,
    FOREIGN KEY (team1_id) REFERENCES Teams(team_id)
                                    ON DELETE CASCADE
                                    ON UPDATE CASCADE,
    FOREIGN KEY (team2_id) REFERENCES Teams(team_id)
                                    ON DELETE CASCADE
                                    ON UPDATE CASCADE
);