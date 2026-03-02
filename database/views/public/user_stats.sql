SELECT
    usuario.id AS user_id,
    usuario.name AS user_name,
    COUNT(post.id) AS post_count
FROM usuario
LEFT JOIN post ON usuario.id = post.author_id
GROUP BY usuario.id, usuario.name