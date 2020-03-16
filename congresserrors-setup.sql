DROP SCHEMA CongressErrors;

CREATE SCHEMA CongressErrors;

USE CongressErrors;
  
CREATE TABLE Systems (
	systemID INT PRIMARY KEY AUTO_INCREMENT,
    systemName VARCHAR(255) UNIQUE NOT NULL
);

INSERT INTO Systems (systemName)
VALUES ('Loader');

CREATE TABLE SystemErrors_Loader (
	loaderErrorID INT PRIMARY KEY AUTO_INCREMENT,
    systemID INT NOT NULL,
    errorDescription VARCHAR(1000) NOT NULL,
    errorPath VARCHAR(1000) NOT NULL,
    CONSTRAINT sysErrLoader_FK FOREIGN KEY (systemID) REFERENCES Systems (systemID),
    CONSTRAINT sysErrLoader_Chk CHECK ((systemID) IN (1)) # should be dynamically set
);
	
    
    
    