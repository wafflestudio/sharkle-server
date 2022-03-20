import factory
from django.test import TestCase
from factory.django import DjangoModelFactory
from rest_framework_simplejwt.tokens import RefreshToken
from board.models import Board
from circle.models import Circle
from article.models import Article
from user.models import User
from rest_framework import status


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    user_id = factory.Sequence(lambda n: "user_id%d" % n)
    username = factory.Sequence(lambda n: "user%d" % n)
    email = factory.LazyAttribute(lambda o: "%s@sharkle.org" % o.username)
    password = "1234"

    @classmethod
    def create(cls, **kwargs):
        user = User.objects.create_user(**kwargs)
        return user


class CircleFactory(DjangoModelFactory):
    class Meta:
        model = Circle

    name = factory.Sequence(lambda n: "Circle %d" % n)
    bio = factory.Sequence(lambda n: "Circle %d bio" % n)
    tag = "sample_tag"


class BoardFactory(DjangoModelFactory):
    class Meta:
        model = Board

    circle = factory.SubFactory(CircleFactory)
    name = "QnA"


class ArticleFactory(DjangoModelFactory):
    class Meta:
        model = Article

    board = factory.SubFactory(BoardFactory)
    author = factory.SubFactory(UserFactory)


# Create your tests here.
class PostArticleTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.board = BoardFactory()
        cls.circle = cls.board.circle
        cls.default_data = {"title": "Announce", "content": "welcome it's a test"}
        cls.user_token = "Bearer " + str(RefreshToken.for_user(cls.user).access_token)

    def test_create_article_success(self):
        data = self.default_data.copy()
        prev_count = Article.objects.count()
        response = self.client.post(
            f"/api/v1/circle/{self.board.circle.id}/board/{self.board.id}/article/",
            data=data,
            content_type="application/json",
            HTTP_AUTHORIZATION=self.user_token,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(prev_count + 1, Article.objects.count())
        response_data = response.json()
        self.assertIn("title", response_data)
        self.assertIn("content", response_data)

    def test_non_existing_id(self):
        data = self.default_data.copy()
        prev_count = Article.objects.count()
        response = self.client.post(
            f"/api/v1/circle/{self.board.circle.id}/board/500/article/",
            data=data,
            content_type="application/json",
            HTTP_AUTHORIZATION=self.user_token,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(prev_count, Article.objects.count())


class GetArticleTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.board = BoardFactory()
        cls.circle = cls.board.circle
        cls.user_token = "Bearer " + str(RefreshToken.for_user(cls.user).access_token)
        cls.article1 = ArticleFactory(title="article1", content="I need rest...")
        cls.article2 = ArticleFactory(
            title="article2", content="Fighting!!!", board=cls.board
        )
        cls.article3 = ArticleFactory(
            title="article3", content="^.^!!!", board=cls.board
        )

    def test_list_article_success(self):
        response = self.client.get(
            f"/api/v1/circle/{self.board.circle.id}/board/{self.board.id}/article/",
            data={},
            content_type="application/json",
            HTTP_AUTHORIZATION=self.user_token,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()

    def test_retrieve_article_success(self):
        response = self.client.get(
            f"/api/v1/circle/{self.board.circle.id}/board/{self.board.id}/article/{self.article1.id}/",
            data={},
            content_type="application/json",
            HTTP_AUTHORIZATION=self.user_token,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual("article1", response_data["title"])
        self.assertEqual("I need rest...", response_data["content"])

    def test_retrieve_article_not_found(self):
        response = self.client.get(
            f"/api/v1/circle/{self.board.circle.id}/board/{self.board.id}/article/500/",
            data={},
            content_type="application/json",
            HTTP_AUTHORIZATION=self.user_token,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UpdateArticleTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.board = BoardFactory()
        cls.circle = cls.board.circle
        cls.my_article = ArticleFactory(
            title="article1", content="I am the author", author=cls.user
        )
        cls.default_data = {"title": "Announce", "content": "welcome it's a test"}
        cls.user_token = "Bearer " + str(RefreshToken.for_user(cls.user).access_token)

    def test_update_article_success(self):
        data = self.default_data.copy()
        response = self.client.put(
            f"/api/v1/circle/{self.board.circle.id}/board/{self.board.id}/article/{self.my_article.id}/",
            data=data,
            content_type="application/json",
            HTTP_AUTHORIZATION=self.user_token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(self.default_data["title"], response_data["title"])
        self.assertEqual(self.default_data["content"], response_data["content"])

    def test_non_existing_id(self):
        data = self.default_data.copy()
        response = self.client.put(
            f"/api/v1/circle/{self.board.circle.id}/board/{self.board.id}/article/500/",
            data=data,
            content_type="application/json",
            HTTP_AUTHORIZATION=self.user_token,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual("article1", self.my_article.title)


class DeleteArticleTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.board = BoardFactory()
        cls.circle = cls.board.circle
        cls.my_article = ArticleFactory(
            title="Bye", content="I will be deleted soon", author=cls.user
        )
        cls.user_token = "Bearer " + str(RefreshToken.for_user(cls.user).access_token)

    def test_update_article_success(self):
        prev_count = Article.objects.count()
        response = self.client.delete(
            f"/api/v1/circle/{self.board.circle.id}/board/{self.board.id}/article/{self.my_article.id}/",
            content_type="application/json",
            HTTP_AUTHORIZATION=self.user_token,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(prev_count - 1, Article.objects.count())

    def test_non_existing_id(self):
        prev_count = Article.objects.count()
        response = self.client.delete(
            f"/api/v1/circle/{self.board.circle.id}/board/{self.board.id}/article/500/",
            content_type="application/json",
            HTTP_AUTHORIZATION=self.user_token,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(prev_count, Article.objects.count())
