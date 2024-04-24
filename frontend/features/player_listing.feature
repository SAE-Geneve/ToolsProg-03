# Created by Minimata at 24/04/2024
Feature: Listing players
  As an API tester
  I want to see all my players
  So that I can have a good idea of database content

  Scenario: List all players
    Given there are players in the database
    When the tool is opened
    Then player list is not empty

