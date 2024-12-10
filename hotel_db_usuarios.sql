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
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(45) NOT NULL,
  `apellido` varchar(45) NOT NULL,
  `fecha_nacimiento` datetime NOT NULL,
  `email` varchar(45) NOT NULL,
  `contrasena` varchar(255) NOT NULL,
  `dni` varchar(20) NOT NULL,
  `rol` varchar(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (9,'Mansilla','Lautaro','2024-11-01 00:00:00','lautaro917@gmail.com','pbkdf2:sha256:600000$Sy3Udu4aEIH5iC6Z$5bedf32c02f61d307765ba88332dfd7776626d894abe187bdf3f3f4d1ea428fa','43254375','empleado'),(12,'Franco','asddsa','2024-11-01 00:00:00','asdsda@gmail.com','pbkdf2:sha256:600000$AuPF0tlCuXEApiYr$a65c6baf1aac330f9fb48e9ad751f2f2a2a399b748ce4c41eb23d9133c59f500','31635681','cliente'),(13,'Mans','Nas','2024-10-11 00:00:00','sdaasd@gmail.com','pbkdf2:sha256:600000$rkp68vHxOJgKkMIc$4f4bddd4facf97b482571158d73271af5417e011ecb6ef0bee1e74286a99dfe5','31635681','cliente'),(20,'Lautaro','Mansilla','2024-11-16 00:00:00','lautaro918@gmail.com','pbkdf2:sha256:600000$ZWkJlDF56ppYEnFn$ee6dc6cdf08f68a816d6aa320f776fd4fe996acddc065cb0170f4382d2c19eb4','432543759','administrador'),(21,'Nahuel','Iuzzolino','1997-06-25 00:00:00','nahuel.iuzzolino@gmail.com','pbkdf2:sha256:600000$W0AJvtVQaBfYxLah$05cc11d7a3e64aa2bcf0dc4399592195b8e2f507b59afa3e80bfabd29ba3f3cb','40143295','administrador');
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
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
