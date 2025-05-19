/*
EXAMPLE PROCEDURES

-- Drop procedures if they already exist
DROP PROCEDURE IF EXISTS get_all_coaches;
DROP PROCEDURE IF EXISTS insert_coach;
DROP PROCEDURE IF EXISTS delete_coach_by_username;
DROP PROCEDURE IF EXISTS update_coach_nationality;

DELIMITER //

-- Procedure 1: Get all coaches
CREATE PROCEDURE get_all_coaches()
BEGIN
    SELECT * FROM coaches;
END //

-- Procedure 2: Insert a new coach
CREATE PROCEDURE insert_coach(
    IN p_username VARCHAR(255),
    IN p_password VARCHAR(255),
    IN p_name VARCHAR(255),
    IN p_surname VARCHAR(255),
    IN p_nationality VARCHAR(255),
    IN p_date_of_birth DATE
)
BEGIN
    INSERT INTO coaches (username, password, name, surname, nationality, date_of_birth)
    VALUES (p_username, p_password, p_name, p_surname, p_nationality, p_date_of_birth);
END //

-- Procedure 3: Delete a coach by username
CREATE PROCEDURE delete_coach_by_username(
    IN p_username VARCHAR(255)
)
BEGIN
    DELETE FROM coaches WHERE username = p_username;
END //

-- Procedure 4: Update nationality by username
CREATE PROCEDURE update_coach_nationality(
    IN p_username VARCHAR(255),
    IN p_new_nationality VARCHAR(255)
)
BEGIN
    UPDATE coaches
    SET nationality = p_new_nationality
    WHERE username = p_username;
END //

DELIMITER ;
*/

DROP PROCEDURE IF EXISTS CheckUserCredentials;

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

DELIMITER ;