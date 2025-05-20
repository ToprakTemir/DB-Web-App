DROP TRIGGER IF EXISTS CheckMatchConstraints;

DELIMITER //

CREATE TRIGGER CheckMatchConstraints
BEFORE INSERT ON Matches
FOR EACH ROW
BEGIN
    DECLARE conflicting_matches INT;
    DECLARE next_slot CHAR(1);
    DECLARE prev_slot CHAR(1);
    DECLARE slot_num INT;

    -- Check that team1 != team2
    IF NEW.team1_id = NEW.team2_id THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'A team cannot play against itself.';
    END IF;

    -- Safely compute next_slot
    SET slot_num = CONVERT(NEW.time_slot, UNSIGNED INTEGER);
    SET next_slot = CONVERT(slot_num + 1, CHAR);

    -- Check for same or next time_slot conflict at same table
    SELECT COUNT(*) INTO conflicting_matches
    FROM Matches
    WHERE date = NEW.date
      AND hall_id = NEW.hall_id
      AND table_id = NEW.table_id
      AND (time_slot = NEW.time_slot OR time_slot = next_slot OR time_slot = prev_slot);

    IF conflicting_matches > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Conflict: Table already in use at this or next slot.';
    END IF;

    -- Check for arbiter conflict at same or next time slot
    SELECT COUNT(*) INTO conflicting_matches
    FROM Matches
    WHERE date = NEW.date
      AND arbiter_username = NEW.arbiter_username
      AND (time_slot = NEW.time_slot OR time_slot = next_slot OR time_slot = prev_slot);

    IF conflicting_matches > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Conflict: Arbiter already assigned at this or next time slot.';
    END IF;
END //

DELIMITER ;
