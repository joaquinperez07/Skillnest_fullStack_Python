# ERD - BookHub

```mermaid
erDiagram
    USERS ||--o{ BOOKS : "publica (1:N)"
    USERS ||--o{ FAVORITES : "marca"
    BOOKS ||--o{ FAVORITES : "es marcado"

    USERS {
        int id PK
        varchar first_name
        varchar last_name
        varchar email UK
        varchar password
        datetime created_at
        datetime updated_at
    }
    BOOKS {
        int id PK
        varchar title
        varchar author
        varchar genre
        date publication_date
        text description
        int user_id FK
        datetime created_at
        datetime updated_at
    }
    FAVORITES {
        int user_id PK, FK
        int book_id PK, FK
        datetime created_at
    }
```

- **users 1:N books**: un usuario publica muchos libros.
- **users N:M books** (vía `favorites`): un usuario tiene muchos libros favoritos y un libro es favorito de muchos usuarios.
