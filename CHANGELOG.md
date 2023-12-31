# Changelog
Format is loosely related to https://keepachangelog.com/en/1.1.0/.
Version numbers follow this convention:
- Version: `X.Y.Z`
  - `X` is the major version number, related to new functional designs and major UI changes.
  - `Y` is the minor version number, related to new functionalities and major refactors.
  - `Z` is the patch version number, for bug fixes corresponding to the base version.
- Tags:
  - [PRD]: Production executable
  - [FUS]: Functionality, Usability, Supportability.
  - [MVP]: Minimum Viable Product
  - [QAI]: Quallity Assurance Issues
  - [OOP]: Object-oriented Programming
  - [RAS]: Reliability, Availability, and Serviceability (Stability)

## Comments
- (#XX) refers to issue number
- Actions:
  - Hotfix: fix a specific issue. They tend to have small impact over the complete project
  - Added: new feature
  - Fixed: fix issues that may span over the complete project.
  - Changed: existing features which have undergone some improvements.

## [v1.1.1] - [RAS] 2024-01-05
### Added
- Set up `logging` for database operations and runtime exceptions. (#36)

### Changed
- Optimize code performance and standards. (#16)
- Improve security for database operations. (#30)


## [v1.1.0] - [OOP] 2024-01-03
### Added
- Implement strict MVC pattern. (#15)


## [v1.0.0] - [MVP] 2024-01-01
### Added
- Create app UI mockup. (#1)
- Create backend logic for controller and model. (#3)
- Implement data persistence. (#7)
- Implement `Flake8`. (#9)
- Create documenation. (#11)
- Upload mock data to database. (#20)
- Create PDF documentation. (#22)
- Create CHANGELOG. (#13)

### Changed
- Update README.md. (#5)

### Fixed
- Fix layout. (#14)
- Fix `get_graph_data` function to ensure the month is correctly formatted. (#18)
