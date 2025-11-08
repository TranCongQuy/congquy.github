-- SQL Script for Microsoft SQL Server (MSSQL)
-- Author: Chuyên gia lập trình Python
-- Database: weather_app_db (ví dụ)

-- =================================================================
-- MỨC ĐỘ CƠ BẢN
-- =================================================================

-- Bảng 1: locations
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[locations]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[locations](
        [id] INT PRIMARY KEY IDENTITY(1,1), -- IDENTITY(1,1) tương đương AUTO_INCREMENT
        [city_name] NVARCHAR(255) NOT NULL,
        [country] NVARCHAR(10) NOT NULL,
        [latitude] DECIMAL(9, 6) NOT NULL,
        [longitude] DECIMAL(9, 6) NOT NULL,
        CONSTRAINT UQ_city_country UNIQUE (city_name, country) -- Ràng buộc UNIQUE
    );
END
GO

-- Bảng 2: weather_cache
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[weather_cache]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[weather_cache](
        [id] INT PRIMARY KEY IDENTITY(1,1),
        [location_id] INT NOT NULL,
        [timestamp] DATETIME NOT NULL,
        [temperature] FLOAT NULL,
        [humidity] INT NULL,
        [description] NVARCHAR(255) NULL,
        [wind_speed] FLOAT NULL,
        [icon_code] NVARCHAR(10) NULL,
        [data_json] NVARCHAR(MAX) NULL, -- Dùng NVARCHAR(MAX) để lưu chuỗi JSON
        
        -- Khóa ngoại liên kết tới bảng locations
        FOREIGN KEY (location_id) REFERENCES [dbo].[locations](id) ON DELETE CASCADE
    );
END
GO

-- =================================================================
-- MỨC ĐỘ NÂNG CAO
-- =================================================================

-- Bảng 3: users
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[users]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[users](
        [id] INT PRIMARY KEY IDENTITY(1,1),
        [username] NVARCHAR(100) NOT NULL UNIQUE,
        [email] NVARCHAR(255) NOT NULL UNIQUE,
        [password_hash] NVARCHAR(255) NOT NULL
    );
END
GO

-- Bảng 4: favorite_locations
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[favorite_locations]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[favorite_locations](
        [user_id] INT NOT NULL,
        [location_id] INT NOT NULL,
        
        -- Khóa chính kết hợp từ hai cột
        PRIMARY KEY (user_id, location_id),
        
        -- Các khóa ngoại
        FOREIGN KEY (user_id) REFERENCES [dbo].[users](id) ON DELETE CASCADE,
        FOREIGN KEY (location_id) REFERENCES [dbo].[locations](id) ON DELETE CASCADE
    );
END
GO