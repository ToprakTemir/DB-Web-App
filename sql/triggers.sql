/*
EXAMPLE TRIGGERS


-- Drop triggers if they exist
DROP TRIGGER IF EXISTS before_user_insert;
DROP TRIGGER IF EXISTS after_user_insert;

-- Use custom delimiter to allow compound statements
DELIMITER //

-- Trigger 1: Uppercase username before insert
CREATE TRIGGER before_user_insert
BEFORE INSERT ON coaches
FOR EACH ROW
BEGIN
    SET NEW.username = UPPER(NEW.username);
END //

-- Trigger 2: Log user insert into audit_log table
CREATE TRIGGER after_user_insert
AFTER INSERT ON coaches
FOR EACH ROW
BEGIN
    INSERT INTO titles (title_ID, title_name) VALUES (1, 'example_title');
END //

DELIMITER ;
*/
