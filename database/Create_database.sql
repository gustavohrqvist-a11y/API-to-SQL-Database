
USE jobbit;

CREATE TABLE companies (
    company_id INT PRIMARY KEY AUTO_INCREMENT,
    company_name VARCHAR(255) NOT NULL,
    company_website VARCHAR(255)
);

CREATE TABLE jobs (
    job_id INT PRIMARY KEY AUTO_INCREMENT,
    api_job_id VARCHAR(255) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    url VARCHAR(255),
    published_date DATETIME,
    company_id INT NOT NULL,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE applications (
    application_id INT PRIMARY KEY AUTO_INCREMENT,
    job_id INT NOT NULL UNIQUE,
    status VARCHAR(255) NOT NULL,
    applied_date DATETIME,
    notes TEXT,
    FOREIGN KEY (job_id) REFERENCES jobs(job_id)
);

SELECT * FROM jobs;


show TABLES;

DESCRIBE companies;

select * from companies;

select * from jobs;