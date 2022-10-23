from django.conf import settings

from .base_testcase import PostTestCase


class GroupModelTest(PostTestCase):
    def test_group_model_have_correct_object_names(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        expected_object_name = self.group.title
        self.assertEqual(expected_object_name, str(self.group))


class PostModelTest(PostTestCase):
    def test_post_model_have_correct_object_names(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        expected_object_name = self.post.text[: settings.MAX_LENGTH_STR]
        self.assertEqual(expected_object_name, str(self.post))

    def test_post_model_verbose_name(self):
        """Проверяем, что verbose_name у модели Post
        в полях совпадает с ожидаемым.
        """
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    expected_value,
                )

    def test_post_model_help_text(self):
        """Проверяем, что help_text у модели Post
        в полях совпадает с ожидаемым.
        """
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text, expected_value
                )
