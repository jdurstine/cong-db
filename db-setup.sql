DROP SCHEMA Congress;

CREATE SCHEMA Congress;

USE Congress;

CREATE TABLE Votes (
	voteID VARCHAR(16) PRIMARY KEY,
    updatedAt DATE NOT NULL,
    type VARCHAR(255) NOT NULL,
    subject VARCHAR(1000) NOT NULL,
    sourceURL VARCHAR(255) NOT NULL,
    session INT NOT NULL,
    resultText VARCHAR(1000) NOT NULL,
    result VARCHAR(1000) NOT NULL,
    requires VARCHAR(25) NOT NULL,
    question VARCHAR (1000) NOT NULL,
    number INT NOT NULL
);

CREATE TABLE CongressMembers (
	memberID VARCHAR(10) PRIMARY KEY,
    displayName VARCHAR(50) NOT NULL,
    party CHAR(1) NOT NULL,
    state CHAR(2) NOT NULL
);

CREATE TABLE MemberVotes (
	voteID VARCHAR(16) NOT NULL,
    memberID VARCHAR(10) NOT NULL,
    memberVote VARCHAR(100) NOT NULL,
    CONSTRAINT MemberVotes_PK PRIMARY KEY (voteID, memberID),
    CONSTRAINT MemberVotes_voteID_FK FOREIGN KEY (voteID) REFERENCES Votes (voteID),
    CONSTRAINT MemberVotes_memberID_FK FOREIGN KEY (memberID) REFERENCES CongressMembers (memberID)
);