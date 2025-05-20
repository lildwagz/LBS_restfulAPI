
CREATE USER IF NOT EXISTS 'app_user'@'%' IDENTIFIED BY 'Str0ngP@ssw0rd!2024';
GRANT ALL PRIVILEGES ON library_prod.* TO 'app_user'@'%';
FLUSH PRIVILEGES;


CREATE TABLE `users` (
    `id` int NOT NULL AUTO_INCREMENT,
    `username` varchar(50) NOT NULL,
    `password` varchar(255) NOT NULL,
    `role` enum('admin','user') NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `username` (`username`)
);

CREATE TABLE `books` (
    `id` int NOT NULL AUTO_INCREMENT,
    `judul` varchar(100) NOT NULL,
    `pengarang` varchar(50) NOT NULL,
    `stok` int NOT NULL,
    `tahun_terbit` int NOT NULL,
    PRIMARY KEY (`id`)
);

CREATE TABLE `peminjaman` (
    `id` int NOT NULL AUTO_INCREMENT,
    `user_id` int NOT NULL,
    `book_id` int NOT NULL,
    `tgl_pinjam` date NOT NULL,
    `tgl_kembali` date DEFAULT NULL,
    `status` enum('dipinjam','dikembalikan') NOT NULL,
    PRIMARY KEY (`id`),
    KEY `user_id` (`user_id`),
    KEY `book_id` (`book_id`),
    CONSTRAINT `fk_peminjaman_books` FOREIGN KEY (`book_id`)
        REFERENCES `books` (`id`) ON DELETE CASCADE,
    CONSTRAINT `peminjaman_ibfk_1` FOREIGN KEY (`user_id`)
        REFERENCES `users` (`id`),
    CONSTRAINT `peminjaman_ibfk_2` FOREIGN KEY (`book_id`)
        REFERENCES `books` (`id`)
);

FLUSH PRIVILEGES;

INSERT INTO books (judul, pengarang, stok, tahun_terbit) VALUES
                                                             ('Laskar Pelangi', 'Andrea Hirata', 15, 2005),
                                                             ('Bumi Manusia', 'Pramoedya Ananta Toer', 12, 1980),
                                                             ('Harry Potter and the Philosopher''s Stone', 'J.K. Rowling', 25, 1997),
                                                             ('The Lord of the Rings', 'J.R.R. Tolkien', 18, 1954),
                                                             ('To Kill a Mockingbird', 'Harper Lee', 20, 1960),
                                                             ('1984', 'George Orwell', 22, 1949),
                                                             ('Pride and Prejudice', 'Jane Austen', 15, 1813),
                                                             ('The Great Gatsby', 'F. Scott Fitzgerald', 17, 1925),
                                                             ('The Catcher in the Rye', 'J.D. Salinger', 10, 1951),
                                                             ('The Alchemist', 'Paulo Coelho', 30, 1988),
                                                             ('The Da Vinci Code', 'Dan Brown', 28, 2003),
                                                             ('The Hobbit', 'J.R.R. Tolkien', 19, 1937),
                                                             ('The Hunger Games', 'Suzanne Collins', 23, 2008),
                                                             ('The Kite Runner', 'Khaled Hosseini', 14, 2003),
                                                             ('The Little Prince', 'Antoine de Saint-Exupéry', 35, 1943),
                                                             ('The Girl on the Train', 'Paula Hawkins', 16, 2015),
                                                             ('Gone Girl', 'Gillian Flynn', 18, 2012),
                                                             ('The Book Thief', 'Markus Zusak', 13, 2005),
                                                             ('Fahrenheit 451', 'Ray Bradbury', 11, 1953),
                                                             ('The Chronicles of Narnia', 'C.S. Lewis', 20, 1950),
                                                             ('Animal Farm', 'George Orwell', 15, 1945),
                                                             ('The Fault in Our Stars', 'John Green', 22, 2012),
                                                             ('The Shining', 'Stephen King', 19, 1977),
                                                             ('The Godfather', 'Mario Puzo', 17, 1969),
                                                             ('The Martian', 'Andy Weir', 14, 2011),
                                                             ('The Silent Patient', 'Alex Michaelides', 12, 2019),
                                                             ('Educated', 'Tara Westover', 10, 2018),
                                                             ('Becoming', 'Michelle Obama', 25, 2018),
                                                             ('Sapiens: A Brief History of Humankind', 'Yuval Noah Harari', 20, 2011),
                                                             ('Atomic Habits', 'James Clear', 30, 2018),
                                                             ('Dilan 1990', 'Pidi Baiq', 28, 2014),
                                                             ('Perahu Kertas', 'Dee Lestari', 15, 2009),
                                                             ('Negeri 5 Menara', 'Ahmad Fuadi', 18, 2009),
                                                             ('Pulang', 'Tere Liye', 20, 2015),
                                                             ('Ronggeng Dukuh Paruk', 'Ahmad Tohari', 12, 1982),
                                                             ('Ayat-Ayat Cinta', 'Habiburrahman El Shirazy', 25, 2004),
                                                             ('Cinta di Dalam Gelas', 'Andrea Hirata', 14, 2006),
                                                             ('Supernova: Ksatria, Puteri, dan Bintang Jatuh', 'Dee Lestari', 16, 2001),
                                                             ('The Midnight Library', 'Matt Haig', 13, 2020),
                                                             ('Where the Crawdads Sing', 'Delia Owens', 19, 2018),
                                                             ('Rich Dad Poor Dad', 'Robert T. Kiyosaki', 30, 1997),
                                                             ('The Subtle Art of Not Giving a F*ck', 'Mark Manson', 25, 2016),
                                                             ('Think and Grow Rich', 'Napoleon Hill', 20, 1937),
                                                             ('The Power of Habit', 'Charles Duhigg', 18, 2012),
                                                             ('Born a Crime', 'Trevor Noah', 15, 2016),
                                                             ('The Seven Husbands of Evelyn Hugo', 'Taylor Jenkins Reid', 14, 2017),
                                                             ('One Hundred Years of Solitude', 'Gabriel García Márquez', 16, 1967),
                                                             ('Crime and Punishment', 'Fyodor Dostoevsky', 12, 1866),
                                                             ('The Art of War', 'Sun Tzu', 22, -500),  -- Tahun 500 SM
                                                             ('The Diary of a Young Girl', 'Anne Frank', 20, 1947),
                                                             ('The Handmaid''s Tale', 'Margaret Atwood', 17, 1985);


-- INSERT INTO users (username, password, role) VALUES
-- -- Admin (5 orang)
-- ('admin', 'admin', 'admin'),
-- ('sutrisnobachir', 'B4chir!X', 'admin'),
-- ('khofifahindar', 'Kh0f!f4h#', 'admin'),
-- ('ekatjandranegara', '3k4Tjan!', 'admin'),
-- ('tgbaguseko', 'TgB4g5$', 'admin'),
--
-- -- User (45 orang)
-- ('radityadika', 'radityadika', 'user'),
-- ('ajibasuki', 'ajibasuki', 'user'),
-- ('titisjuman', 'titisjuman', 'user'),
-- ('rinisuryono', 'rinisuryono', 'user'),
-- ('aldojonathan', 'aldojonathan', 'user'),
-- ('susipudjiastuti', 'susipudjiastuti', 'user'),
-- ('ekakurniawan', 'ekakurniawan', 'user'),
-- ('lukmanhakim', 'lukmanhakim', 'user'),
-- ('nurhayatisubary', 'nurhayatisubary', 'user'),
-- ('davidjulius', 'davidjulius', 'user'),
-- ('fitriaanggraini', 'fitriaanggraini', 'user'),
-- ('antonioblanco', 'Bl4nc0Ant', 'user'),
-- ('srimulyani', 'Muly4n1', 'user'),
-- ('bambangpamungkas', 'B4mb4ngP', 'user'),
-- ('ratnasarumpaet', 'R4tn4S', 'user'),
-- ('arifinputra', 'Putr4Ar1f', 'user'),
-- ('melatisuryodarmo', 'M3lat1D', 'user'),
-- ('jokowidodo', 'W1d0d0Jk', 'user'),
-- ('sandradewi', 'D3w1S4n', 'user'),
-- ('hendrasetiawan', 'H3ndr4S', 'user'),
-- ('laksmipamuntjak', 'L4ksm1P', 'user'),
-- ('ajisantoso', 'S4nt0s0Aj', 'user'),
-- ('rinanose', 'N0s3R1n', 'user'),
-- ('tulussimatupang', 'Tuluss1m4', 'user'),
-- ('prillylatuconsina', 'Pr1llyLC', 'user'),
-- ('rezarahadian', 'R4h4d14nRz', 'user'),
-- ('dianpelangi', 'P3l4ng1D', 'user'),
-- ('ariobayu', 'B4yuAr1o', 'user'),
-- ('najwashihab', 'Sh1h4bN', 'user'),
-- ('joetaslim', 'T4sl1mJ0', 'user'),
-- ('maudyayunda', '4yund4Mau', 'user'),
-- ('riodewanto', 'D3w4nt0R', 'user'),
-- ('vaneshaprescilla', 'Pr3sc1ll4', 'user'),
-- ('iwanfals', 'F4ls1wan', 'user'),
-- ('rossasinaga', 'S1n4g4Ros', 'user'),
-- ('tretanmuslim', 'Musl1mTr3t', 'user'),
-- ('citrascholastika', 'Sch0l4sT', 'user'),
-- ('judikanababan', 'N4b4b4nJ', 'user'),
-- ('agnesmonica', 'M0n1c4Ag', 'user'),
-- ('armandmaulana', 'M4ul4n4Ar', 'user'),
-- ('gitagutawa', 'Gut4w4G', 'user'),
-- ('andretaulany', 'T4ul4nyAn', 'user'),
-- ('rinirosdiana', 'R0sd1ana', 'user'),
-- ('destamahendra', 'M4h3ndr4D', 'user'),
-- ('sulenugroho', 'Nugr0h0S', 'user'),
-- ('nurularifin', '4r1f1nNur', 'user'),
-- ('ridwankamil', 'K4m1lR1d', 'user'),
-- ('sherinamunaf', 'Mun4fSh3', 'user');



-- INSERT INTO peminjaman (user_id, book_id, tgl_pinjam, tgl_kembali, status)
-- SELECT
--     user_id,
--     book_id,
--     tgl_pinjam,
--     tgl_kembali,
--     IF(tgl_kembali IS NOT NULL, 'dikembalikan', 'dipinjam') AS status
-- FROM (
--          SELECT
--              FLOOR(6 + RAND() * 45) AS user_id, -- User ID 6-50
--              FLOOR(1 + RAND() * 50) AS book_id, -- Book ID 1-50
--              DATE_ADD('2023-01-01', INTERVAL FLOOR(RAND() * 852) DAY) AS tgl_pinjam,
--              CASE
--                  WHEN RAND() < 0.7 THEN
--                      LEAST(
--                              DATE_ADD(DATE_ADD('2023-01-01', INTERVAL FLOOR(RAND() * 852) DAY),
--                                       INTERVAL FLOOR(1 + RAND() * 30) DAY),
--                              '2025-05-02'
--                      )
--                  ELSE NULL
--                  END AS tgl_kembali
--          FROM
--              (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) a
--                  CROSS JOIN
--              (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) b
--                  CROSS JOIN
--              (SELECT 1 UNION SELECT 2) c
--          LIMIT 500
--      ) AS subquery;