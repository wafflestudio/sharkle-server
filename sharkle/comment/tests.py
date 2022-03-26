from django.test import TestCase

# Create your tests here.
import factory
from django.test import TestCase
from factory.django import DjangoModelFactory
from rest_framework_simplejwt.tokens import RefreshToken
from board.models import Board
from circle.models import Circle
from article.models import Article
from comment.models import Comment
from user.models import User
from rest_framework import status

# Duplicated Factories in test.. move to common? or ...
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
    title = factory.Sequence(lambda n: "Title %d" % n)
    content = factory.Sequence(lambda n: "Article content %d" % n)


class CommentFactory(DjangoModelFactory):
    class Meta:
        model = Comment

    article = factory.SubFactory(ArticleFactory)
    author = factory.SubFactory(UserFactory)


# Create your tests here.
class PostCommentTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.article = ArticleFactory(title="Hi", content="leave comment")
        cls.comment = CommentFactory(content="base comment")
        cls.default_data = {"content": "first comment!"}
        cls.user_token = "Bearer " + str(RefreshToken.for_user(cls.user).access_token)

    # article/{id}/comment/?reply_to=~~
    def test_create_comment_success(self):
        data = self.default_data.copy()
        prev_count = Comment.objects.count()
        response = self.client.post(
            f"/api/v1/article/{self.article.id}/comment/",
            data=data,
            content_type="application/json",
            HTTP_AUTHORIZATION=self.user_token,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(prev_count + 1, Comment.objects.count())
        response_data = response.json()
        self.assertIn("content", response_data)

    def test_create_replying_comment_success(self):
        data = self.default_data.copy()
        prev_count = Comment.objects.count()
        response = self.client.post(
            f"/api/v1/article/{self.article.id}/comment/?reply_to={self.comment.id}",
            data=data,
            content_type="application/json",
            HTTP_AUTHORIZATION=self.user_token,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(prev_count + 1, Comment.objects.count())
        response_data = response.json()
        self.assertIn("content", response_data)
        self.assertEqual(response_data["reply_to"], self.comment.id)

    def test_non_existing_article(self):
        data = self.default_data.copy()
        prev_count = Comment.objects.count()
        response = self.client.post(
            f"/api/v1/article/{Article.objects.count()+20}/comment/",
            data=data,
            content_type="application/json",
            HTTP_AUTHORIZATION=self.user_token,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(prev_count, Comment.objects.count())


class GetCommentTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.articleA = ArticleFactory()
        cls.articleB = ArticleFactory()
        cls.comment1A = CommentFactory(content="comment1", article=cls.articleA)
        cls.comment2A = CommentFactory(content="comment2", article=cls.articleA)
        cls.comment1B = CommentFactory(content="comment2", article=cls.articleB)
        cls.user_token = "Bearer " + str(RefreshToken.for_user(cls.user).access_token)

    def test_list_article_success(self):
        response = self.client.get(
            f"/api/v1/article/{self.articleA.id}/comment/",
            data={},
            content_type="application/json",
            HTTP_AUTHORIZATION=self.user_token,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        print(response_data)  # TODO. count?

    def test_retrieve_article_success(self):
        response = self.client.get(
            f"/api/v1/article/{self.articleA.id}/comment/{self.comment1A.id}/",
            data={},
            content_type="application/json",
            HTTP_AUTHORIZATION=self.user_token,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        print(response_data)  # TODO

    def test_retrieve_article_not_found(self):
        response = self.client.get(
            f"/api/v1/article/{self.articleA.id}/comment/{Comment.objects.count()+40}/",
            data={},
            content_type="application/json",
            HTTP_AUTHORIZATION=self.user_token,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
