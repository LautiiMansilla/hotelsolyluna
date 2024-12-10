-- MySQL dump 10.13  Distrib 8.0.22, for Win64 (x86_64)
--
-- Host: localhost    Database: hotel_db
-- ------------------------------------------------------
-- Server version	8.0.39

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
-- Table structure for table `habitaciones`
--

DROP TABLE IF EXISTS `habitaciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `habitaciones` (
  `id` int NOT NULL AUTO_INCREMENT,
  `numero` varchar(10) NOT NULL,
  `tipo` varchar(50) NOT NULL,
  `capacidad` int NOT NULL,
  `estado` varchar(20) DEFAULT 'disponible',
  `precio` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `numero` (`numero`),
  CONSTRAINT `chk_estado` CHECK ((`estado` in (_utf8mb4'disponible',_utf8mb4'reservada',_utf8mb4'mantenimiento')))
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `habitaciones`
--

LOCK TABLES `habitaciones` WRITE;
/*!40000 ALTER TABLE `habitaciones` DISABLE KEYS */;
INSERT INTO `habitaciones` VALUES (1,'1-01','doble',2,'reservada',80000.00),(2,'1-02','doble',2,'reservada',80000.00),(3,'1-03','simple',1,'reservada',50000.00),(4,'1-04','simple',1,'reservada',50000.00),(5,'1-05','doble',2,'reservada',80000.00),(6,'1-06','doble',2,'reservada',80000.00),(7,'1-07','suite',4,'reservada',150000.00),(8,'1-08','doble',2,'disponible',80000.00),(9,'1-09','suite',4,'reservada',150000.00),(10,'1-10','simple',1,'disponible',50000.00),(11,'2-01','simple',1,'disponible',50000.00),(12,'2-02','simple',1,'disponible',50000.00),(13,'2-03','simple',1,'reservada',50000.00),(14,'2-04','suite',4,'disponible',150000.00),(15,'2-05','simple',1,'disponible',50000.00),(16,'2-06','simple',1,'disponible',50000.00),(17,'2-07','simple',1,'disponible',50000.00),(18,'2-08','suite',4,'disponible',150000.00),(19,'2-09','doble',2,'disponible',80000.00),(20,'2-10','simple',1,'reservada',50000.00),(21,'3-01','simple',1,'disponible',50000.00),(22,'3-02','doble',2,'disponible',80000.00),(23,'3-03','doble',2,'disponible',80000.00),(24,'3-04','simple',1,'disponible',50000.00),(25,'3-05','simple',1,'disponible',50000.00),(26,'3-06','simple',1,'disponible',50000.00),(27,'3-07','suite',4,'disponible',150000.00),(28,'3-08','suite',4,'reservada',150000.00),(29,'3-09','simple',1,'disponible',50000.00),(30,'3-10','doble',2,'reservada',80000.00);
/*!40000 ALTER TABLE `habitaciones` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-11-28 18:29:33
