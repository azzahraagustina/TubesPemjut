-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               8.0.30 - MySQL Community Server - GPL
-- Server OS:                    Win64
-- HeidiSQL Version:             12.1.0.6537
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Dumping database structure for db_tk_badak_putih
CREATE DATABASE IF NOT EXISTS `db_tk_badak_putih` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `db_tk_badak_putih`;

-- Dumping structure for table db_tk_badak_putih.tbl_laporan
CREATE TABLE IF NOT EXISTS `tbl_laporan` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username_ortu` varchar(50) NOT NULL,
  `nama_anak` varchar(100) NOT NULL,
  `kelas` varchar(20) DEFAULT NULL,
  `semester` varchar(50) DEFAULT NULL,
  `tb` varchar(10) DEFAULT NULL,
  `bb` varchar(10) DEFAULT NULL,
  `narasi_agama` text,
  `narasi_karakter` text,
  `narasi_fisik` text,
  `narasi_kognitif` text,
  `narasi_bahasa` text,
  `narasi_sosem` text,
  `narasi_seni` text,
  `karakter_1` varchar(5) DEFAULT NULL,
  `karakter_2` varchar(5) DEFAULT NULL,
  `karakter_3` varchar(5) DEFAULT NULL,
  `karakter_4` varchar(5) DEFAULT NULL,
  `karakter_5` varchar(5) DEFAULT NULL,
  `kes_mata` varchar(50) DEFAULT NULL,
  `kes_telinga` varchar(50) DEFAULT NULL,
  `kes_gigi` varchar(50) DEFAULT NULL,
  `kes_rapian` varchar(50) DEFAULT NULL,
  `catatan_guru` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Data exporting was unselected.

-- Dumping structure for table db_tk_badak_putih.tbl_ppdb
CREATE TABLE IF NOT EXISTS `tbl_ppdb` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nama_anak` varchar(100) NOT NULL,
  `nama_ortu` varchar(100) NOT NULL,
  `no_hp` varchar(20) NOT NULL,
  `alamat` text NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Data exporting was unselected.

-- Dumping structure for table db_tk_badak_putih.tbl_users
CREATE TABLE IF NOT EXISTS `tbl_users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nama` varchar(100) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('admin','guru','orang_tua') NOT NULL DEFAULT 'orang_tua',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Data exporting was unselected.

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
