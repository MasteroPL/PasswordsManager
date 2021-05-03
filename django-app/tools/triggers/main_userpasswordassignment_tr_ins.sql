
DROP TRIGGER main_userpasswordassignment_tr_ins;

DELIMITER //

CREATE TRIGGER main_userpasswordassignment_tr_ins BEFORE INSERT ON main_userpasswordassignment
FOR EACH ROW
BEGIN
	IF EXISTS (SELECT 1 FROM main_password WHERE main_password.owner_id = NEW.user_id) THEN
		SIGNAL SQLSTATE '45000'
			SET MESSAGE_TEXT = 'Duplicate for assignment to password. Password main owner cannot be assigned to the password again';
	END IF;
END//

DELIMITER ;