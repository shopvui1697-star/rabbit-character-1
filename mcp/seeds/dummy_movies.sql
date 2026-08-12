-- Sample movies for local dev / embedding tests.
-- Safe to re-run: skips insert when any rows already exist.

INSERT INTO data_archive_movie_master (
    title,
    original_title,
    overview,
    release_date,
    poster_path,
    backdrop_path,
    source,
    vote_average,
    vote_count,
    genre_ids,
    product_type,
    runtime
)
SELECT *
FROM (VALUES
    (
        'Spirited Away',
        '千と千尋の神隠し',
        'A young girl finds herself in a magical world of spirits and must work to free herself and her parents.',
        '2001-07-20',
        'https://image.tmdb.org/t/p/w500/39wmItIWsg5sZMyRUHLkWBcuVCM.jpg',
        NULL,
        'https://www.themoviedb.org/movie/129',
        8.5,
        14000,
        '16,14',
        'movie',
        125
    ),
    (
        'Your Name',
        '君の名は。',
        'Two teenagers share a profound, magical connection upon discovering they are swapping bodies.',
        '2016-08-26',
        'https://image.tmdb.org/t/p/w500/q719jXXEhI1am6qdBIAbpZBecbg.jpg',
        NULL,
        'https://www.themoviedb.org/movie/372058',
        8.6,
        9700,
        '16,18,14',
        'movie',
        106
    ),
    (
        'Tokyo Story',
        '東京物語',
        'An elderly couple visit their children and grandchildren in the city, but find them too busy to spend time with them.',
        '1953-11-03',
        'https://image.tmdb.org/t/p/w500/sNFMpKmJxEOI4fWmfsYkd9laG6M.jpg',
        NULL,
        'https://www.themoviedb.org/movie/18148',
        8.2,
        1300,
        '18',
        'movie',
        136
    ),
    (
        'Parasite',
        '기생충',
        'Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan.',
        '2019-05-30',
        'https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYFhjTp93U9j.jpg',
        NULL,
        'https://www.themoviedb.org/movie/496243',
        8.5,
        12000,
        '18,53,35',
        'movie',
        132
    ),
    (
        'The Matrix',
        'The Matrix',
        'A computer hacker learns about the true nature of reality and his role in the war against its controllers.',
        '1999-03-31',
        'https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpPEzn4.jpg',
        NULL,
        'https://www.themoviedb.org/movie/603',
        8.2,
        24000,
        '28,878',
        'movie',
        136
    ),
    (
        'Inception',
        'Inception',
        'A thief who steals corporate secrets through dream-sharing technology is offered a chance at redemption.',
        '2010-07-16',
        'https://image.tmdb.org/t/p/w500/9oTUk0DGiYJ1R5DeIzqD2mJAXqQ.jpg',
        NULL,
        'https://www.themoviedb.org/movie/27205',
        8.4,
        33000,
        '28,878,12',
        'movie',
        148
    ),
    (
        'My Neighbor Totoro',
        'となりのトトロ',
        'Two sisters discover friendly forest spirits near their new home in the countryside.',
        '1988-04-16',
        'https://image.tmdb.org/t/p/w500/rtGDOeG9LzoerkDGZQ9U4DD9qlA.jpg',
        NULL,
        'https://www.themoviedb.org/movie/8392',
        8.1,
        7200,
        '16,14,10751',
        'movie',
        86
    ),
    (
        'Blade Runner 2049',
        'Blade Runner 2049',
        'A young blade runner discovers a secret that could plunge society into chaos.',
        '2017-10-06',
        'https://image.tmdb.org/t/p/w500/gajva2L0rPYkEWjzgFlBXCAVBE5.jpg',
        NULL,
        'https://www.themoviedb.org/movie/335984',
        7.8,
        9800,
        '878,18,9648',
        'movie',
        164
    )
) AS seed (
    title,
    original_title,
    overview,
    release_date,
    poster_path,
    backdrop_path,
    source,
    vote_average,
    vote_count,
    genre_ids,
    product_type,
    runtime
)
WHERE NOT EXISTS (SELECT 1 FROM data_archive_movie_master LIMIT 1);
