# README

cong-db is a data pipeline combined with a data model that connects congressional information in a relational database. Right now this project only attempts to answer the question "Who voted for what?". Once setup and turned on it will automatically initiate daily data pulls and database imports to keep the database as up to date as possible.

## Dependencies

This project builds off [unitedstates/congress](https://github.com/unitedstates/congress) and consumes the data scraped from congressional websites using that tool.

Additionally it relies on having an install of mysql and the appropriate mysql tools installed.

This project has only been tested on Ubuntu.

## Database

Congress is the primary schema for holding congressional data. It is composed of three tables - Votes, MemberVotes, and CongressMembers. Votes holds vote specific information and CongressMembers holds data for individual congressional members. The two are connected by an M-M mapping table which tallies how each individual congress member voted on a particular vote.

<p align="center">
  <img src="https://github.com/jdurstine/cong-db/blob/master/congress-erd.png">
</p>

Although not complete, the CongressErrors schema provides scaffolding for more robust error tracking outside of logging critical failures. The table SystemErrors_Loader keeps track of any issues that occur while importing scraped data into the database which did not result from an unhandled error. The errors stored here typically result from unexpected input from the side of the scraper. The path to the offending data and the specific error are logged. The systems table provides a way of tracking import errors down to additional systems if those systems are added.

<p align="center">
  <img src="https://github.com/jdurstine/cong-db/blob/master/congresserror-erd.png"
</p>


