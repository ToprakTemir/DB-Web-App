DROP PROCEDURE IF EXISTS CheckUserCredentials;
DROP PROCEDURE IF EXISTS InsertPlayer;
DROP PROCEDURE IF EXISTS InsertCoach;
DROP PROCEDURE IF EXISTS InsertPlayerTeam;
DROP PROCEDURE IF EXISTS InsertCoachCertification;
DROP PROCEDURE IF EXISTS InsertArbiter;
DROP PROCEDURE IF EXISTS InsertArbiterCertification;
DROP PROCEDURE IF EXISTS InsertMatch;

DELIMITER //

CREATE PROCEDURE CheckUserCredentials(
    IN in_username VARCHAR(255),
    IN in_password VARCHAR(255),
    OUT matched BOOLEAN,
    OUT matched_table VARCHAR(50)
)
BEGIN
    SET matched = FALSE;
    SET matched_table = NULL;

    -- Check DBManagers
    IF EXISTS (SELECT 1 FROM DBManagers WHERE username = in_username AND password = in_password) THEN
        SET matched = TRUE;
        SET matched_table = 'DBManagers';
    -- Check Players
    ELSEIF EXISTS (SELECT 1 FROM Players WHERE username = in_username AND password = in_password) THEN
        SET matched = TRUE;
        SET matched_table = 'Players';
    -- Check Coaches
    ELSEIF EXISTS (SELECT 1 FROM Coaches WHERE username = in_username AND password = in_password) THEN
        SET matched = TRUE;
        SET matched_table = 'Coaches';
    -- Check Arbiters
    ELSEIF EXISTS (SELECT 1 FROM Arbiters WHERE username = in_username AND password = in_password) THEN
        SET matched = TRUE;
        SET matched_table = 'Arbiters';
    END IF;
END //





CREATE PROCEDURE InsertPlayer(
    IN in_username VARCHAR(50),
    IN in_password VARCHAR(50),
    IN in_name VARCHAR(50),
    IN in_surname VARCHAR(50),
    IN in_nationality VARCHAR(50),
    IN in_date_of_birth VARCHAR(50),
    IN in_fide_ID INT,
    IN in_elo_rating INT,
    IN in_title_id INT
)
BEGIN
    INSERT INTO Players (
        username,
        password,
        name,
        surname,
        nationality,
        date_of_birth,
        fide_ID,
        elo_rating,
        title_id
    ) VALUES (
        in_username,
        in_password,
        in_name,
        in_surname,
        in_nationality,
        (STR_TO_DATE(in_date_of_birth, '%d-%m-%Y')),
        in_fide_ID,
        in_elo_rating,
        in_title_id
    );
END //




CREATE PROCEDURE InsertCoach(
    IN in_username VARCHAR(50),
    IN in_password VARCHAR(50),
    IN in_name VARCHAR(50),
    IN in_surname VARCHAR(50),
    IN in_nationality VARCHAR(50),
    IN in_team_id INT,
    IN in_contract_start VARCHAR(50),
    IN in_contract_finish VARCHAR(50)
)
BEGIN
    INSERT INTO Coaches (
        username,
        password,
        name,
        surname,
        nationality,
        team_id,
        contract_start,
        contract_finish
    ) VALUES (
        in_username,
        in_password,
        in_name,
        in_surname,
        in_nationality,
        in_team_id,
        (STR_TO_DATE(in_contract_start, '%d-%m-%Y')),
        (STR_TO_DATE(in_contract_finish, '%d-%m-%Y'))
    );
END //




CREATE PROCEDURE InsertPlayerTeam(
    IN in_username VARCHAR(50),
    IN in_team_id INT
)
BEGIN
    INSERT INTO PlayerTeams (
        username,
        team_id
    ) VALUES (
        in_username,
        in_team_id
    );
END //




CREATE PROCEDURE InsertCoachCertification(
    IN in_coach_username VARCHAR(50),
    IN in_certification VARCHAR(50)
)
BEGIN
    INSERT INTO CoachCertifications (
        coach_username,
        certification
    ) VALUES (
        in_coach_username,
        in_certification
    );
END //



CREATE PROCEDURE InsertArbiter(
    IN in_username VARCHAR(50),
    IN in_password VARCHAR(50),
    IN in_name VARCHAR(50),
    IN in_surname VARCHAR(50),
    IN in_nationality VARCHAR(50),
    IN in_experience_level VARCHAR(50)
)
BEGIN
    INSERT INTO Arbiters (
        username,
        password,
        name,
        surname,
        nationality,
        experience_level
    ) VALUES (
        in_username,
        in_password,
        in_name,
        in_surname,
        in_nationality,
        in_experience_level
    );
END //



CREATE PROCEDURE InsertArbiterCertification(
    IN in_username VARCHAR(50),
    IN in_certification VARCHAR(50)
)
BEGIN
    INSERT INTO ArbiterCertifications (
        username,
        certification
    ) VALUES (
        in_username,
        in_certification
    );
END //



CREATE PROCEDURE InsertMatch(
    IN in_match_id INT,
    IN in_date VARCHAR(50),
    IN in_time_slot ENUM('1', '2', '3', '4'),
    IN in_hall_id INT,
    IN in_table_id INT,
    IN in_team1_id INT,
    IN in_team2_id INT,
    IN in_arbiter_username VARCHAR(50),
    IN in_rating FLOAT
)
BEGIN
    INSERT INTO Matches (
        match_id, 
        date, 
        time_slot, 
        hall_id, 
        table_id,
        team1_id, 
        team2_id, 
        arbiter_username, 
        rating
    )
    VALUES (
        in_match_id, 
        (STR_TO_DATE(in_date, '%d-%m-%Y')), 
        in_time_slot, 
        in_hall_id, 
        in_table_id,
        in_team1_id, 
        in_team2_id, 
        in_arbiter_username, 
        in_rating
    );
END //

DELIMITER ;