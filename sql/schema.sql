CREATE DATABASE IF NOT EXISTS ChessDB;
USE ChessDB;

CREATE TABLE Players(
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(50) NOT NULL,
    name VARCHAR(50),
    surname VARCHAR(50),
    nationality VARCHAR(50) NOT NULL,
    date_of_birth DATE,
    fide_ID INT,
    elo_rating INT,
    CHECK (elo_rating >= 1000)
);

CREATE TABLE Titles(
    title_ID INT PRIMARY KEY,
    title_name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE Player_Title_Pairs(
    player_username VARCHAR(50) PRIMARY KEY,
    title_id INT NOT NULL,
    FOREIGN KEY (player_username) REFERENCES Players(username)
                              ON DELETE CASCADE
                              ON UPDATE CASCADE,
    FOREIGN KEY (title_id) REFERENCES Titles(title_ID)
                                ON DELETE CASCADE
                                ON UPDATE CASCADE
);

CREATE TABLE Coaches(
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(50) NOT NULL,
    name VARCHAR(50),
    surname VARCHAR(50),
    nationality VARCHAR(50) NOT NULL,
    date_of_birth DATE
);

CREATE TABLE Teams_and_Contracts(
    team_ID INT PRIMARY KEY,
    team_name VARCHAR(50) NOT NULL,

    contract_start DATE NOT NULL,
    contract_finish DATE NOT NULL,
    CHECK (contract_start < contract_finish),

    coach_username VARCHAR(50) NOT NULL,
    UNIQUE (coach_username),
    FOREIGN KEY (coach_username) REFERENCES Coaches(username)
                              ON UPDATE CASCADE
);

CREATE TABLE Sponsors(
    sponsor_ID INT PRIMARY KEY,
    sponsor_name VARCHAR(50) NOT NULL
);

CREATE TABLE Sponsorships(
    team_ID INT PRIMARY KEY,
    sponsor_ID INT NOT NULL,
    FOREIGN KEY (team_ID) REFERENCES Teams_and_Contracts(team_ID)
                              ON DELETE CASCADE
                              ON UPDATE CASCADE,
    FOREIGN KEY (sponsor_ID) REFERENCES Sponsors(sponsor_ID)
                                ON DELETE CASCADE
                                ON UPDATE CASCADE
);

# We can't enforce the participation constraint of Player Entity in the Team-Player relation, because we are not allowed to add the trigger to this table to auto-add new created players to this table.
CREATE TABLE Team_Players(
    team_ID INT NOT NULL,
    player_username VARCHAR(50) NOT NULL,
    PRIMARY KEY (team_ID, player_username),
    FOREIGN KEY (team_ID) REFERENCES Teams_and_Contracts(team_ID)
                              ON DELETE CASCADE
                              ON UPDATE CASCADE,
    FOREIGN KEY (player_username) REFERENCES Players(username)
                              ON DELETE CASCADE
                              ON UPDATE CASCADE
);

CREATE TABLE Expertise_Areas(
    area_name VARCHAR(50) PRIMARY KEY
);

CREATE TABLE Coach_Expertise_Pairs(
    username VARCHAR(50) NOT NULL,
    area_name VARCHAR(50) NOT NULL, # we can't enforce the participation constraint of the coach in the 'has coach certificate' relation in the ER diagram, instead we make this notnull to avoid meaningless entries
    PRIMARY KEY (username, area_name),
    FOREIGN KEY (username) REFERENCES Coaches(username)
                                ON DELETE CASCADE
                                ON UPDATE CASCADE,
    FOREIGN KEY (area_name) REFERENCES Expertise_Areas(area_name)
                                ON DELETE CASCADE
                                ON UPDATE CASCADE
);

CREATE TABLE Coach_Certificates(
    area_name VARCHAR(50) PRIMARY KEY
);

CREATE TABLE Coach_Certificate_Pairs(
      coach_username VARCHAR(50) NOT NULL,
      area_name VARCHAR(50) NOT NULL, # we can't enforce the participation constraint of the coach in the 'has coach certificate' relation in the ER diagram, instead we make this notnull to avoid meaningless entries
      PRIMARY KEY (coach_username, area_name),
      FOREIGN KEY (coach_username) REFERENCES Coaches(username)
                                    ON DELETE CASCADE
                                    ON UPDATE CASCADE,
      FOREIGN KEY (area_name) REFERENCES Coach_Certificates(area_name)
                                    ON DELETE CASCADE
                                    ON UPDATE CASCADE
);

CREATE TABLE Arbiters(
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(50) NOT NULL,
    name VARCHAR(50),
    surname VARCHAR(50),
    nationality VARCHAR(50) NOT NULL,

    experience_level ENUM('Beginner', 'Intermediate', 'Advanced') NOT NULL
);

CREATE TABLE Arbiter_Certificates(
    certificate_name VARCHAR(50) PRIMARY KEY
);

CREATE TABLE Arbiter_Certificate_Pairs(
    arbiter_username VARCHAR(50) NOT NULL,
    certificate_name VARCHAR(50) NOT NULL, # we can't enforce the participation constraint of the arbiter in the 'has arbiter certificate' relation in the ER diagram, instead we make this notnull to avoid meaningless entries
    PRIMARY KEY (arbiter_username, certificate_name),
    FOREIGN KEY (arbiter_username) REFERENCES Arbiters(username)
                              ON DELETE CASCADE
                              ON UPDATE CASCADE,
    FOREIGN KEY (certificate_name) REFERENCES Arbiter_Certificates(certificate_name)
                              ON DELETE CASCADE
                              ON UPDATE CASCADE
);

CREATE TABLE Halls(
      hall_ID INT PRIMARY KEY,
      hall_name VARCHAR(50) NOT NULL,
      hall_capacity INT NOT NULL,
      hall_country VARCHAR(50) NOT NULL,
      UNIQUE (hall_name)
);


CREATE TABLE Tables(
       table_ID INT PRIMARY KEY,
       hall_ID INT NOT NULL,

       FOREIGN KEY (hall_ID) REFERENCES Halls(hall_ID)
           ON DELETE CASCADE
           ON UPDATE CASCADE
);

CREATE TABLE Tournaments(
        tournament_ID INT PRIMARY KEY,
        tournament_name VARCHAR(50) NOT NULL,
        start_date DATE NOT NULL,
        end_date DATE NOT NULL,
        format VARCHAR(50) NOT NULL,
        chief_arbiter_username VARCHAR(50) NOT NULL,

        FOREIGN KEY (chief_arbiter_username) REFERENCES Arbiters(username)
            ON DELETE RESTRICT
            ON UPDATE CASCADE

    # here we should enforce that a tournament has at least one match or at least one hall, but we can't do that because we aren't allowed to add triggers to this table
);


CREATE TABLE Tournament_Hall_Pairs(
        tournament_ID INT NOT NULL,
        hall_ID INT NOT NULL,
        PRIMARY KEY (tournament_ID, hall_ID),
        FOREIGN KEY (tournament_ID) REFERENCES Tournaments(tournament_ID)
          ON DELETE CASCADE
          ON UPDATE CASCADE,
        FOREIGN KEY (hall_ID) REFERENCES Halls(hall_ID)
          ON DELETE CASCADE
          ON UPDATE CASCADE
);

CREATE TABLE Matches(
    match_ID INT PRIMARY KEY,
    date DATE NOT NULL,
    time_slot ENUM('1', '2', '3', '4') NOT NULL,
    result ENUM('W', 'B', 'D') NOT NULL, # W: White, B: Black, D: Draw

    white_player_username VARCHAR(50) NOT NULL,
    black_player_username VARCHAR(50) NOT NULL,
    white_player_team_ID INT NOT NULL,
    black_player_team_ID INT NOT NULL,

    arbiter_username VARCHAR(50) NOT NULL,
    rating ENUM('1', '2', '3', '4', '5', '6', '7', '8', '9', '10') NOT NULL,

    hall_ID INT NOT NULL,
    table_ID INT NOT NULL,
    UNIQUE (date, time_slot, table_ID), # makes sure that there is only one match in a table at a given time slot
    UNIQUE (date, time_slot, arbiter_username), # makes sure that an arbiter oversees only one match at any given time
    UNIQUE(date, time_slot, white_player_username), # makes sure players play only one match at any given time
    UNIQUE(date, time_slot, black_player_username),

    tournament_ID INT NOT NULL,

    FOREIGN KEY (white_player_team_ID, white_player_username) REFERENCES Team_Players(team_ID, player_username),
    FOREIGN KEY ( black_player_team_ID, black_player_username) REFERENCES Team_Players(team_ID, player_username),
    FOREIGN KEY (arbiter_username) REFERENCES Arbiters(username),
    FOREIGN KEY (hall_ID) REFERENCES Halls(hall_ID),
    FOREIGN KEY (table_ID) REFERENCES Tables(table_ID),
    FOREIGN KEY (tournament_ID) REFERENCES Tournaments(tournament_ID),

    CHECK (white_player_username != black_player_username),
    CHECK (white_player_team_ID != black_player_team_ID)
);