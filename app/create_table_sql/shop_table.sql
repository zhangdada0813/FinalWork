/*
 Navicat Premium Data Transfer

 Source Server         : local_mysql
 Source Server Type    : MySQL
 Source Server Version : 80034 (8.0.34)
 Source Host           : localhost:3306
 Source Schema         : price_compare

 Target Server Type    : MySQL
 Target Server Version : 80034 (8.0.34)
 File Encoding         : 65001

 Date: 05/12/2023 23:31:57
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for shop_table
-- ----------------------------
DROP TABLE IF EXISTS `shop_table`;
CREATE TABLE `shop_table`  (
  `shop_no` int NOT NULL,
  `shop_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `shop_distance_max` double NULL DEFAULT NULL,
  `credit_grade` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `delivery_type` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `delivery_type_text` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `shop_distance` double NULL DEFAULT NULL,
  `minimum_order_amount` int NULL DEFAULT NULL,
  `main_products` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `monthly_sales` int NULL DEFAULT NULL,
  `insure` int NULL DEFAULT NULL,
  `evaluate_score` int NULL DEFAULT NULL,
  PRIMARY KEY (`shop_no`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
