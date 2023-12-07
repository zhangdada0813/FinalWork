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

 Date: 05/12/2023 23:32:04
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for shop_detail_table
-- ----------------------------
DROP TABLE IF EXISTS `shop_detail_table`;
CREATE TABLE `shop_detail_table`  (
  `goods_no` int NOT NULL,
  `goods_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `sell_price` decimal(10, 2) NULL DEFAULT NULL,
  `goods_type_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `goods_unit` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `spec_status` set('0','1') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT '',
  `spec_no` int NOT NULL,
  `good_unit_remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `monthly_sales` int NULL DEFAULT NULL,
  `shop_no` int NULL DEFAULT NULL,
  PRIMARY KEY (`goods_no`, `spec_no`) USING BTREE,
  INDEX `foreign_key_shop_no`(`shop_no` ASC) USING BTREE,
  CONSTRAINT `foreign_key_shop_no` FOREIGN KEY (`shop_no`) REFERENCES `shop_table` (`shop_no`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
