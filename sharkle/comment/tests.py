from django.test import TestCase

# Create your tests here.
import factory
from django.test import TestCase
from factory.django import DjangoModelFactory
from rest_framework_simplejwt.tokens import RefreshToken
from board.models import Board
from circle.models import Circle, UserCircle_Member
from article.models import Article
from comment.models import Comment
from user.models import User
from rest_framework import status

# Duplicated Factories in test.. move to common? or ...
class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: "user%d" % n)
    email = factory.LazyAttribute(lambda o: "%s@sharkle.org" % o.username)
    password = "1234"


class CircleFactory(DjangoModelFactory):
    class Meta:
        model = Circle

    name = factory.Sequence(lambda n: "Circle %d" % n)
    bio = factory.Sequence(lambda n: "Circle %d bio" % n)
    tag = "sample_tag"


class MemberFactory(DjangoModelFactory):
    class Meta:
        model = UserCircle_Member

    user = factory.SubFactory(UserFactory)
    circle = factory.SubFactory(CircleFactory)


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

    def test_list_comment_success(self):
        response = self.client.get(
            f"/api/v1/article/{self.articleA.id}/comment/",
            data={},
            content_type="application/json",
            HTTP_AUTHORIZATION=self.user_token,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()

        # TODO. count?

    def test_retrieve_comment_success(self):
        response = self.client.get(
            f"/api/v1/article/{self.articleA.id}/comment/{self.comment1A.id}/",
            data={},
            content_type="application/json",
            HTTP_AUTHORIZATION=self.user_token,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data["content"], "comment1")

    def test_retrieve_comment_not_found(self):
        response = self.client.get(
            f"/api/v1/article/{self.articleA.id}/comment/{Comment.objects.count()+40}/",
            data={},
            content_type="application/json",
            HTTP_AUTHORIZATION=self.user_token,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UpdateCommentTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.member = MemberFactory(is_manager=True)
        cls.circle = cls.member.circle
        cls.board = BoardFactory(circle=cls.circle)
        cls.manager = cls.member.user  # manager of circle
        cls.author = (
            UserFactory()
        )  # member of same circle, the author of the target comment
        cls.member_author = MemberFactory(circle=cls.circle, user=cls.author)
        cls.outsider = UserFactory()

        cls.article = ArticleFactory(board=cls.board)
        cls.comment = CommentFactory(
            content="comment", article=cls.article, author=cls.author
        )

        cls.manager_token = "Bearer " + str(
            RefreshToken.for_user(cls.manager).access_token
        )
        cls.author_token = "Bearer " + str(
            RefreshToken.for_user(cls.author).access_token
        )
        cls.outsider_token = "Bearer " + str(
            RefreshToken.for_user(cls.outsider).access_token
        )

    def test_non_existing_id(self):
        data = {"content": "update comment"}
        response = self.client.put(
            f"/api/v1/article/{self.article.id}/comment/{Comment.objects.count()+30}/",
            data=data,
            content_type="application/json",
            HTTP_AUTHORIZATION=self.manager_token,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual("comment", self.comment.content)

    def test_update_comment_by_author_success(self):
        data = {"content": "update comment"}
        response = self.client.put(
            f"/api/v1/article/{self.article.id}/comment/{self.comment.id}/",
            data=data,
            content_type="application/json",
            HTTP_AUTHORIZATION=self.author_token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual("update comment", response_data["content"])

    def test_update_comment_by_manager_success(self):
        data = {"content": "update comment"}
        response = self.client.put(
            f"/api/v1/article/{self.article.id}/comment/{self.comment.id}/",
            data=data,
            content_type="application/json",
            HTTP_AUTHORIZATION=self.manager_token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual("update comment", response_data["content"])

    def test_update_comment_by_outsider_fail(self):
        data = {"content": "no permission to update"}
        response = self.client.put(
            f"/api/v1/article/{self.article.id}/comment/{self.comment.id}/",
            data=data,
            content_type="application/json",
            HTTP_AUTHORIZATION=self.outsider_token,
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DeleteCommentTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.member = MemberFactory(is_manager=True)
        cls.circle = cls.member.circle
        cls.board = BoardFactory(circle=cls.circle)
        cls.manager = cls.member.user  # manager of circle
        cls.author = (
            UserFactory()
        )  # member of same circle, the author of the target comment
        cls.member_author = MemberFactory(circle=cls.circle, user=cls.author)
        cls.outsider = UserFactory()

        cls.article1 = ArticleFactory(board=cls.board)
        cls.article2 = ArticleFactory(board=cls.board)
        cls.comment1 = CommentFactory(
            content="comment", article=cls.article1, author=cls.author
        )
        cls.comment2 = CommentFactory(
            content="comment", article=cls.article2, author=cls.author
        )
        cls.comment3 = CommentFactory(
            content="comment", article=cls.article1, author=cls.author
        )
        cls.reply = CommentFactory(
            content="comment",
            article=cls.article1,
            author=cls.author,
            reply_to=cls.comment3,
        )

        cls.manager_token = "Bearer " + str(
            RefreshToken.for_user(cls.manager).access_token
        )
        cls.author_token = "Bearer " + str(
            RefreshToken.for_user(cls.author).access_token
        )
        cls.outsider_token = "Bearer " + str(
            RefreshToken.for_user(cls.outsider).access_token
        )

    def test_delete_comment_by_author_success(self):
        prev_comment_count = Comment.objects.count()
        prev_article_count = Article.objects.count()

        response = self.client.delete(
            f"/api/v1/article/{self.article1.id}/comment/{self.comment1.id}/",
            content_type="application/json",
            HTTP_AUTHORIZATION=self.author_token,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(prev_comment_count - 1, Comment.objects.count())
        self.assertEqual(prev_article_count, Article.objects.count())

    def test_delete_comment_with_replies_by_manager_success(self):
        prev_comment_count = Comment.objects.count()
        prev_article_count = Article.objects.count()

        response = self.client.delete(
            f"/api/v1/article/{self.article1.id}/comment/{self.comment3.id}/",
            content_type="application/json",
            HTTP_AUTHORIZATION=self.manager_token,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            prev_comment_count, Comment.objects.count()
        )  # comment count does not change
        self.assertEqual("삭제된 댓글입니다.", Comment.objects.get(id=self.comment3.id).content)

    # delete article -> comment deleted
    def test_cascade_comment_success(self):
        prev_comment_count = Comment.objects.count()
        prev_article_count = Article.objects.count()
        response = self.client.delete(
            f"/api/v1/circle/{self.article2.board.circle.id}/board/{self.article2.board.id}/article/{self.article2.id}/",
            content_type="application/json",
            HTTP_AUTHORIZATION=self.author_token,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(prev_comment_count - 1, Comment.objects.count())
        self.assertEqual(prev_article_count - 1, Article.objects.count())

    def test_non_existing_id(self):
        prev_count = Comment.objects.count()
        response = self.client.delete(
            f"/api/v1/article/{self.article1.id}/comment/{Comment.objects.count()+30}/",
            content_type="application/json",
            HTTP_AUTHORIZATION=self.manager_token,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(prev_count, Comment.objects.count())
