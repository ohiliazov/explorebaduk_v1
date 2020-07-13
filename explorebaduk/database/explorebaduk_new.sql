-- phpMyAdmin SQL Dump
-- version 4.8.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 25, 2020 at 05:40 PM
-- Server version: 10.1.37-MariaDB
-- PHP Version: 7.3.0

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `explorebaduk_new`
--

-- --------------------------------------------------------

--
-- Table structure for table `friends`
--

CREATE TABLE `friends` (
  `ID` int(10) NOT NULL,
  `User_ID` int(10) NOT NULL,
  `Friend_ID` int(10) NOT NULL,
  `Muted` tinyint(1) NOT NULL,
  `Blocked` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `messages`
--

CREATE TABLE `messages` (
  `Message_ID` int(10) NOT NULL,
  `Message` text CHARACTER SET utf8mb4 NOT NULL,
  `Sender` int(10) NOT NULL,
  `Receiver` int(10) NOT NULL,
  `Sent` int(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `notifications`
--

CREATE TABLE `notifications` (
  `Notification_ID` int(10) NOT NULL,
  `Notification_Type` int(3) NOT NULL,
  `Sender` int(10) NOT NULL,
  `Receiver` int(10) NOT NULL,
  `Added` int(10) NOT NULL,
  `Content` text,
  `Status` tinyint(1) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `notification_types`
--

CREATE TABLE `notification_types` (
  `Notification_Type_ID` int(4) NOT NULL,
  `Notification_Type` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `signin_tokens`
--

CREATE TABLE `signin_tokens` (
  `ID` int(11) NOT NULL,
  `Token` varchar(64) NOT NULL,
  `User_ID` int(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `social_comments`
--

CREATE TABLE `social_comments` (
  `Comment_ID` int(10) NOT NULL,
  `Content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `Posted` int(10) NOT NULL,
  `Likes` int(10) NOT NULL DEFAULT '0',
  `User_ID` int(10) NOT NULL,
  `Post_ID` int(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `social_comments_likes`
--

CREATE TABLE `social_comments_likes` (
  `ID` int(10) NOT NULL,
  `Comment_ID` int(10) NOT NULL,
  `User_ID` int(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `social_posts`
--

CREATE TABLE `social_posts` (
  `Post_ID` int(10) NOT NULL,
  `User_ID` int(10) NOT NULL,
  `Content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `Likes` int(10) NOT NULL DEFAULT '0',
  `Posted` int(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `social_posts_likes`
--

CREATE TABLE `social_posts_likes` (
  `ID` int(10) NOT NULL,
  `Post_ID` int(10) NOT NULL,
  `User_ID` int(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `subscription_plans`
--

CREATE TABLE `subscription_plans` (
  `ID` int(11) NOT NULL,
  `Plan` varchar(255) NOT NULL,
  `Title` varchar(255) NOT NULL,
  `Price` decimal(4,2) NOT NULL,
  `Description` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `teachers_biographies`
--

CREATE TABLE `teachers_biographies` (
  `ID` int(10) NOT NULL,
  `Teacher_ID` int(10) NOT NULL,
  `Biography` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `teachers_paypals`
--

CREATE TABLE `teachers_paypals` (
  `ID` int(10) NOT NULL,
  `Teacher_ID` int(10) NOT NULL,
  `PayPal` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `teachers_plans`
--

CREATE TABLE `teachers_plans` (
  `ID` int(10) NOT NULL,
  `Teacher_ID` int(10) NOT NULL,
  `Plan` varchar(255) NOT NULL,
  `Price` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `User_ID` int(10) NOT NULL,
  `First_Name` varchar(60) NOT NULL,
  `Last_Name` varchar(60) NOT NULL,
  `Email` varchar(255) NOT NULL,
  `Username` varchar(255) NOT NULL,
  `Password` varchar(255) NOT NULL,
  `User_Type` tinyint(1) NOT NULL DEFAULT '0',
  `Player_Type` tinyint(1) NOT NULL DEFAULT '0',
  `Avatar` varchar(255) NOT NULL,
  `Country` varchar(60) NOT NULL,
  `Town` varchar(60) NOT NULL,
  `Post_Code` varchar(60) NOT NULL,
  `Address` text NOT NULL,
  `Date_Registered` int(10) NOT NULL,
  `Date_Birth` date NOT NULL,
  `Membership` tinyint(1) NOT NULL DEFAULT '0',
  `EB_Supporter` tinyint(1) NOT NULL DEFAULT '0',
  `Rating` float NOT NULL,
  `Puzzle_rating` float NOT NULL DEFAULT '0',
  `Num_wins` int(7) NOT NULL DEFAULT '0',
  `Num_losses` int(7) NOT NULL DEFAULT '0',
  `Jigo` int(7) DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `users_activity`
--

CREATE TABLE `users_activity` (
  `ID` int(10) NOT NULL,
  `User_ID` int(10) NOT NULL,
  `Last_Activity` int(10) NOT NULL,
  `Status` tinyint(1) NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `users_pictures`
--

CREATE TABLE `users_pictures` (
  `Picture_ID` int(10) NOT NULL,
  `Picture` varchar(255) NOT NULL,
  `User_ID` int(10) NOT NULL,
  `Post_ID` int(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `users_purchased_teachers_plans`
--

CREATE TABLE `users_purchased_teachers_plans` (
  `ID` varchar(25) NOT NULL,
  `Plan_ID` int(10) NOT NULL,
  `Payer` int(10) NOT NULL,
  `Payee` int(10) NOT NULL,
  `Created` varchar(25) NOT NULL,
  `Payer_ID` varchar(25) NOT NULL,
  `Payer_Email` varchar(255) NOT NULL,
  `Payer_First_Name` varchar(255) NOT NULL,
  `Payer_Last_Name` varchar(255) NOT NULL,
  `Status` tinyint(1) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `users_subscriptions`
--

CREATE TABLE `users_subscriptions` (
  `ID` varchar(25) NOT NULL,
  `User_ID` int(10) NOT NULL,
  `Subscription` int(10) NOT NULL,
  `Created` varchar(25) NOT NULL,
  `Payer_ID` varchar(25) NOT NULL,
  `Payer_Email` varchar(255) NOT NULL,
  `First_Name` varchar(255) NOT NULL,
  `Last_Name` varchar(255) NOT NULL,
  `Expire` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `friends`
--
ALTER TABLE `friends`
  ADD PRIMARY KEY (`ID`);

--
-- Indexes for table `game`
--
ALTER TABLE `game`
  ADD PRIMARY KEY (`Game_ID`);

--
-- Indexes for table `game_spectators`
--
ALTER TABLE `game_spectators`
  ADD PRIMARY KEY (`ID`),
  ADD KEY `Game_ID` (`Game_ID`),
  ADD KEY `User_ID` (`User_ID`);

--
-- Indexes for table `messages`
--
ALTER TABLE `messages`
  ADD PRIMARY KEY (`Message_ID`);

--
-- Indexes for table `notifications`
--
ALTER TABLE `notifications`
  ADD PRIMARY KEY (`Notification_ID`),
  ADD KEY `Notification_Type` (`Notification_Type`);

--
-- Indexes for table `notification_types`
--
ALTER TABLE `notification_types`
  ADD PRIMARY KEY (`Notification_Type_ID`);

--
-- Indexes for table `signin_tokens`
--
ALTER TABLE `signin_tokens`
  ADD PRIMARY KEY (`ID`),
  ADD KEY `User_ID` (`User_ID`);

--
-- Indexes for table `social_comments`
--
ALTER TABLE `social_comments`
  ADD PRIMARY KEY (`Comment_ID`);

--
-- Indexes for table `social_comments_likes`
--
ALTER TABLE `social_comments_likes`
  ADD PRIMARY KEY (`ID`);

--
-- Indexes for table `social_posts`
--
ALTER TABLE `social_posts`
  ADD PRIMARY KEY (`Post_ID`);

--
-- Indexes for table `social_posts_likes`
--
ALTER TABLE `social_posts_likes`
  ADD PRIMARY KEY (`ID`);

--
-- Indexes for table `subscription_plans`
--
ALTER TABLE `subscription_plans`
  ADD PRIMARY KEY (`ID`);

--
-- Indexes for table `teachers_biographies`
--
ALTER TABLE `teachers_biographies`
  ADD PRIMARY KEY (`ID`);

--
-- Indexes for table `teachers_paypals`
--
ALTER TABLE `teachers_paypals`
  ADD PRIMARY KEY (`ID`);

--
-- Indexes for table `teachers_plans`
--
ALTER TABLE `teachers_plans`
  ADD PRIMARY KEY (`ID`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`User_ID`);

--
-- Indexes for table `users_activity`
--
ALTER TABLE `users_activity`
  ADD PRIMARY KEY (`ID`);

--
-- Indexes for table `users_pictures`
--
ALTER TABLE `users_pictures`
  ADD PRIMARY KEY (`Picture_ID`);

--
-- Indexes for table `users_purchased_teachers_plans`
--
ALTER TABLE `users_purchased_teachers_plans`
  ADD PRIMARY KEY (`ID`);

--
-- Indexes for table `users_subscriptions`
--
ALTER TABLE `users_subscriptions`
  ADD PRIMARY KEY (`ID`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `friends`
--
ALTER TABLE `friends`
  MODIFY `ID` int(10) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `game_spectators`
--
ALTER TABLE `game_spectators`
  MODIFY `ID` int(10) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `messages`
--
ALTER TABLE `messages`
  MODIFY `Message_ID` int(10) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `notifications`
--
ALTER TABLE `notifications`
  MODIFY `Notification_ID` int(10) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `notification_types`
--
ALTER TABLE `notification_types`
  MODIFY `Notification_Type_ID` int(4) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `signin_tokens`
--
ALTER TABLE `signin_tokens`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `social_comments`
--
ALTER TABLE `social_comments`
  MODIFY `Comment_ID` int(10) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `social_comments_likes`
--
ALTER TABLE `social_comments_likes`
  MODIFY `ID` int(10) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `social_posts`
--
ALTER TABLE `social_posts`
  MODIFY `Post_ID` int(10) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `social_posts_likes`
--
ALTER TABLE `social_posts_likes`
  MODIFY `ID` int(10) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `subscription_plans`
--
ALTER TABLE `subscription_plans`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `teachers_biographies`
--
ALTER TABLE `teachers_biographies`
  MODIFY `ID` int(10) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `teachers_paypals`
--
ALTER TABLE `teachers_paypals`
  MODIFY `ID` int(10) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `teachers_plans`
--
ALTER TABLE `teachers_plans`
  MODIFY `ID` int(10) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `User_ID` int(10) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `users_activity`
--
ALTER TABLE `users_activity`
  MODIFY `ID` int(10) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `users_pictures`
--
ALTER TABLE `users_pictures`
  MODIFY `Picture_ID` int(10) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `notifications`
--
ALTER TABLE `notifications`
  ADD CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`Notification_Type`) REFERENCES `notification_types` (`Notification_Type_ID`);

--
-- Constraints for table `signin_tokens`
--
ALTER TABLE `signin_tokens`
  ADD CONSTRAINT `signin_tokens_ibfk_1` FOREIGN KEY (`User_ID`) REFERENCES `users` (`User_ID`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
