-- =============================================================================
-- Project Tracking Management System - Database Setup Script
-- For WAMP MySQL on Windows
-- =============================================================================

-- Create database with utf8mb4 character set
CREATE DATABASE IF NOT EXISTS `project_tracking`
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- Use the database
USE `project_tracking`;

-- Create application user
-- Note: Use a strong password in production!
CREATE USER IF NOT EXISTS 'ptms_user'@'localhost' 
    IDENTIFIED BY 'ptms_password';

-- Grant all privileges on the database to the user
GRANT ALL PRIVILEGES ON `project_tracking`.* 
    TO 'ptms_user'@'localhost';

-- Grant table creation and modification privileges
GRANT CREATE, ALTER, DROP, INDEX ON `project_tracking`.* 
    TO 'ptms_user'@'localhost';

-- Flush privileges to apply changes
FLUSH PRIVILEGES;

-- Show created database and user info
SELECT 
    'Database created successfully' AS status,
    DATABASE() AS current_database,
    @@character_set_database AS charset,
    @@collation_database AS collation;

SELECT 
    'User granted privileges' AS status,
    user AS username,
    host AS host
FROM mysql.user 
WHERE user = 'ptms_user';

-- Show all databases to confirm
SHOW DATABASES LIKE 'project%';
