-- MySQL dump 10.13  Distrib 8.0.44, for Linux (x86_64)
--
-- Host: localhost    Database: electronics_store
-- ------------------------------------------------------
-- Server version	8.0.44-0ubuntu0.24.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Dumping data for table `newsletter_subscribers`
--

LOCK TABLES `newsletter_subscribers` WRITE;
/*!40000 ALTER TABLE `newsletter_subscribers` DISABLE KEYS */;
INSERT INTO `newsletter_subscribers` (`id`, `email`, `status`, `confirm_token`, `confirmed_at`, `unsubscribed_at`, `created_at`, `updated_at`) VALUES (1,'jonasi@gmail.com','subscribed',NULL,NULL,NULL,'2025-08-21 13:35:29','2025-08-21 13:35:29'),(2,'joemtaika@gmail.com','subscribed',NULL,NULL,NULL,'2025-08-21 13:41:12','2025-12-07 15:14:56'),(5,'zandasinoia@gmail.com','subscribed',NULL,NULL,NULL,'2025-08-28 14:04:45','2025-08-28 14:04:45'),(6,'mzolo@gmail.com','subscribed',NULL,NULL,NULL,'2025-09-12 05:50:31','2025-09-12 05:50:31'),(7,'joermtaika@gmail.com','subscribed',NULL,NULL,NULL,'2025-09-29 04:51:28','2025-09-29 04:51:28'),(8,'gotokoto@gmail.com','subscribed',NULL,NULL,NULL,'2025-11-02 07:05:48','2025-11-02 07:05:48'),(9,'josaka@gmail.com','subscribed',NULL,NULL,NULL,'2025-11-06 12:49:13','2025-11-06 12:49:13');
/*!40000 ALTER TABLE `newsletter_subscribers` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-02-02 10:46:23
