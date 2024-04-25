# Created by const at 25/04/2024
Feature:
  As an administrator,
  I want to see all players
  so that it reflects the state of the database.

  Scenario: empty db
    Given the db is empty
    When the app is opened
    Then the list appears empty

  Scenario: non-empty db
    Given the db is not empty
    When the app is opened
    Then the list shows player names