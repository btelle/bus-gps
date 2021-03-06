-- MySQL Script generated by MySQL Workbench
-- Sun Oct 21 10:31:28 2018
-- Model: Bus GPS    Version: 1.0
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema busgps
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema busgps
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `busgps` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci ;
USE `busgps` ;

-- -----------------------------------------------------
-- Table `busgps`.`line`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `busgps`.`line` ;

CREATE TABLE IF NOT EXISTS `busgps`.`line` (
  `id` VARCHAR(60) NOT NULL COMMENT '',
  `title` VARCHAR(255) NOT NULL COMMENT '',
  `color` VARCHAR(50) NULL COMMENT '',
  `direction_1` VARCHAR(50) NOT NULL COMMENT '',
  `direction_2` VARCHAR(50) NOT NULL COMMENT '',
  PRIMARY KEY (`id`)  COMMENT '')
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `busgps`.`bus`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `busgps`.`bus` ;

CREATE TABLE IF NOT EXISTS `busgps`.`bus` (
  `id` VARCHAR(60) NOT NULL COMMENT '',
  `api_key` VARCHAR(45) NOT NULL COMMENT '',
  `line_id` VARCHAR(60) NULL COMMENT '',
  `created_at` DATETIME NOT NULL COMMENT '',
  PRIMARY KEY (`id`)  COMMENT '',
  UNIQUE INDEX `api_key_UNIQUE` (`api_key` ASC)  COMMENT '',
  INDEX `bus_line_fk_idx` (`line_id` ASC)  COMMENT '',
  CONSTRAINT `bus_line_fk`
    FOREIGN KEY (`line_id`)
    REFERENCES `busgps`.`line` (`id`)
    ON DELETE SET NULL
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `busgps`.`location`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `busgps`.`location` ;

CREATE TABLE IF NOT EXISTS `busgps`.`location` (
  `id` VARCHAR(60) NOT NULL COMMENT '',
  `bus_id` VARCHAR(60) NOT NULL COMMENT '',
  `latitude` FLOAT NOT NULL COMMENT '',
  `longitude` FLOAT NOT NULL COMMENT '',
  `direction` VARCHAR(50) NOT NULL COMMENT '',
  `published_at` DATETIME NOT NULL DEFAULT NOW() COMMENT '',
  PRIMARY KEY (`id`)  COMMENT '',
  INDEX `location_bus_fk_idx` (`bus_id` ASC)  COMMENT '',
  INDEX `location_published_at_idx` (`published_at` ASC)  COMMENT '',
  CONSTRAINT `location_bus_fk`
    FOREIGN KEY (`bus_id`)
    REFERENCES `busgps`.`bus` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
