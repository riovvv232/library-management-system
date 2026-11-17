def test_root_and_openapi(client):
    assert client.get("/").json()["docs"] == "/docs"

    docs_response = client.get("/docs")
    assert docs_response.status_code == 200

    schema = client.get("/openapi.json").json()
    assert "/books" in schema["paths"]
    assert "/books/{book_id}" in schema["paths"]


def test_create_and_get_book(client):
    response = client.post(
        "/books", json={"title": "三体", "author": "刘慈欣", "year": 2006}
    )
    assert response.status_code == 201
    created = response.json()
    assert created["id"] == 1
    assert created["title"] == "三体"

    fetched = client.get("/books/1")
    assert fetched.status_code == 200
    assert fetched.json() == created


def test_list_books(client):
    client.post("/books", json={"title": "A", "author": "Author A"})
    client.post("/books", json={"title": "B", "author": "Author B", "year": 2020})

    books = client.get("/books").json()
    assert [book["title"] for book in books] == ["A", "B"]


def test_update_book(client):
    created = client.post(
        "/books", json={"title": "旧标题", "author": "作者", "year": 2000}
    ).json()

    response = client.put(
        f"/books/{created['id']}",
        json={"title": "新标题", "year": 2024},
    )
    assert response.status_code == 200
    updated = response.json()
    assert updated["title"] == "新标题"
    assert updated["author"] == "作者"
    assert updated["year"] == 2024

    assert client.get(f"/books/{created['id']}").json() == updated


def test_delete_book(client):
    created = client.post("/books", json={"title": "临时书", "author": "作者"}).json()

    response = client.delete(f"/books/{created['id']}")
    assert response.status_code == 204
    assert client.get(f"/books/{created['id']}").status_code == 404
    assert client.get("/books").json() == []


def test_get_update_delete_missing_book_return_404(client):
    assert client.get("/books/999").status_code == 404
    assert client.put("/books/999", json={"title": "新书"}).status_code == 404
    assert client.delete("/books/999").status_code == 404


def test_invalid_payload_return_422(client):
    assert client.post("/books", json={"title": "", "author": "作者"}).status_code == 422
    assert client.post("/books", json={"author": "作者"}).status_code == 422
    assert (
        client.put("/books/1", json={"year": "不是数字"}).status_code == 422
    )
