# Первая задача
all_users = {'id3', 'id5', 'id9', 'id8', 'id2', 'id1', 'id4', 'id6', 'id7', 'id10'}
offline_users = {'id3', 'id9', 'id7', 'id2', 'id4', 'id6'}

online_users = all_users - offline_users
print("Пользователи online:", online_users)

# Вторая задача
readers_books = {'id3', 'id5', 'id9', 'id8', 'id2', 'id1'}
readers_magazines = {'id8', 'id2', 'id1', 'id4', 'id6', 'id7', 'id10'}

both_readers = readers_books & readers_magazines
print("Читают и книги, и газеты:", both_readers)
