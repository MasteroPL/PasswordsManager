
DROP TRIGGER main_password_tr_upd;

DELIMITER //

CREATE TRIGGER main_password_tr_upd BEFORE UPDATE ON main_password
FOR EACH ROW
BEGIN
	IF EXISTS (SELECT 1 FROM main_userpasswordassignment WHERE main_userpasswordassignment.user_id = NEW.owner_id) THEN
		SIGNAL SQLSTATE '45000'
			SET MESSAGE_TEXT = 'Duplicate for assignment to password. Password main owner cannot be assigned to the password again';
	END IF;
END//

DELIMITER ;