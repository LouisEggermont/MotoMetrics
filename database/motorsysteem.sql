-- MySQL dump 10.13  Distrib 8.0.32, for Win64 (x86_64)
--
-- Host: localhost    Database: motorsysteem
-- ------------------------------------------------------
-- Server version	8.0.32

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `action`
--

DROP TABLE IF EXISTS `action`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `action` (
  `id` int NOT NULL,
  `name` varchar(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `action`
--

LOCK TABLES `action` WRITE;
/*!40000 ALTER TABLE `action` DISABLE KEYS */;
INSERT INTO `action` VALUES (1,'save accel'),(2,'save tilt'),(3,'save location'),(4,'save speed'),(5,'save ambient temp'),(6,'save engine temp');
/*!40000 ALTER TABLE `action` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `device`
--

DROP TABLE IF EXISTS `device`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `device` (
  `id` int NOT NULL,
  `name` varchar(45) NOT NULL,
  `description` varchar(150) DEFAULT NULL,
  `type` varchar(20) NOT NULL,
  `measurement_unit` varchar(20) DEFAULT NULL,
  `merk` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`,`type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `device`
--

LOCK TABLES `device` WRITE;
/*!40000 ALTER TABLE `device` DISABLE KEYS */;
INSERT INTO `device` VALUES (1,'MPU-6050 accelerometer','I²C 3-axis accelerometer','sensor','G',NULL),(2,'MPU-6050 tilt','I²C 3-axis gyroscope','sensor','°',NULL),(3,'LDR','light detecting resistor','sensor',NULL,NULL),(4,'PA1616S GPS','GPS location','sensor',NULL,'Adafruit'),(5,'PA1616S speed','GPS speed','sensor','km/u','Adafruit'),(6,'MAX6675','SPI thermocouple module HW-550 V1.2','sensor','°C',NULL),(7,'DS18B20','One-wire temperature','sensor','°C',NULL),(8,'lighting','12V led lighting','actuator',NULL,NULL),(9,'buzzer','12V piezo buzzer','actuator',NULL,'Velleman'),(10,'display','OLED 0.96\" I²C display V1.1','actuator',NULL,NULL);
/*!40000 ALTER TABLE `device` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `history`
--

DROP TABLE IF EXISTS `history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deviceid` int NOT NULL,
  `actionid` int NOT NULL,
  `rideid` int NOT NULL,
  `value` decimal(32,0) NOT NULL,
  `time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `FK10_idx` (`actionid`),
  KEY `FK20_idx` (`deviceid`),
  KEY `FK03_idx` (`rideid`),
  CONSTRAINT `FK01` FOREIGN KEY (`actionid`) REFERENCES `action` (`id`),
  CONSTRAINT `FK02` FOREIGN KEY (`deviceid`) REFERENCES `device` (`id`),
  CONSTRAINT `FK03` FOREIGN KEY (`rideid`) REFERENCES `ride` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `history`
--

LOCK TABLES `history` WRITE;
/*!40000 ALTER TABLE `history` DISABLE KEYS */;
/*!40000 ALTER TABLE `history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ride`
--

DROP TABLE IF EXISTS `ride`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ride` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) DEFAULT NULL,
  `start_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `stop_time` datetime DEFAULT NULL,
  `distance` float DEFAULT NULL,
  `max_speed` float DEFAULT NULL,
  `avg_speed` float DEFAULT NULL,
  `max_amb_temp` float DEFAULT NULL,
  `avg_amb_temp` float DEFAULT NULL,
  `max_eng_temp` float DEFAULT NULL,
  `avg_eng_temp` float DEFAULT NULL,
  `start_location` decimal(32,0) DEFAULT NULL,
  `stop_location` decimal(32,0) DEFAULT NULL,
  `max_left_tilt` float DEFAULT NULL,
  `max_right_tilt` float DEFAULT NULL,
  `max_accel` float DEFAULT NULL,
  `min_accel` float DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ride`
--

LOCK TABLES `ride` WRITE;
/*!40000 ALTER TABLE `ride` DISABLE KEYS */;
/*!40000 ALTER TABLE `ride` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-06-21 15:26:08
