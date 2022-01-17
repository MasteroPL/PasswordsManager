SELECT DISTINCT `auth_user`.`id`,
    `auth_user`.`password`,
    `auth_user`.`last_login`,
    `auth_user`.`is_superuser`,
    `auth_user`.`username`,
    `auth_user`.`first_name`,
    `auth_user`.`last_name`,
    `auth_user`.`email`,
    `auth_user`.`is_staff`,
    `auth_user`.`is_active`,
    `auth_user`.`date_joined`
FROM `auth_user`
WHERE (
        `auth_user`.`id` IN (
            SELECT V0.`user_id`
            FROM `main_userpasswordshare` V0
            WHERE V0.`user_password_id` IN (
                    SELECT U0.`password_id`
                    FROM `main_userpassword` U0
                        INNER JOIN `main_genericpassword` U1 ON (U0.`password_id` = U1.`id`)
                    WHERE U1.`title` LIKE BINARY a %
                )
        )
        OR `auth_user`.`id` IN (
            SELECT U0.`user_id`
            FROM `main_userpassword` U0
                INNER JOIN `main_genericpassword` U1 ON (U0.`password_id` = U1.`id`)
            WHERE U1.`title` LIKE BINARY a %
        )
    )