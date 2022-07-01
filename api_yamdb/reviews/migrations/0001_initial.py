# Generated by Django 2.2.16 on 2022-06-30 09:33

import api.validators
from django.conf import settings
import django.contrib.auth.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('role', models.CharField(choices=[('admin', 'admin'), ('moderator', 'moderator'), ('user', 'user')], default='user', max_length=5, verbose_name='роль')),
                ('bio', models.TextField(blank=True, verbose_name='биография')),
                ('username', models.CharField(max_length=150, unique=True, verbose_name='имя')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email')),
                ('confirmation_code', models.CharField(blank=True, max_length=70, null=True, unique=True, verbose_name='confirmation_code')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'пользователь',
                'verbose_name_plural': 'пользователи',
                'ordering': ['username'],
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='название категории')),
                ('slug', models.SlugField(unique=True, verbose_name='ссылка')),
            ],
            options={
                'verbose_name': 'категория',
                'verbose_name_plural': 'категории',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='название жанра')),
                ('slug', models.SlugField(unique=True, verbose_name='ссылка')),
            ],
            options={
                'verbose_name': 'жанр',
                'verbose_name_plural': 'жанры',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='GenreTitle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('genre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='genre_titles', to='reviews.Genre', verbose_name='жанр')),
            ],
            options={
                'verbose_name': 'жанр произведения',
                'verbose_name_plural': 'жанры произведений',
            },
        ),
        migrations.CreateModel(
            name='Title',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250, verbose_name='название')),
                ('year', models.PositiveSmallIntegerField(blank=True, null=True, validators=[api.validators.validate_year], verbose_name='год')),
                ('description', models.TextField(blank=True, null=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='titles', to='reviews.Category', verbose_name='категория')),
                ('genre', models.ManyToManyField(through='reviews.GenreTitle', to='reviews.Genre', verbose_name='жанр')),
            ],
            options={
                'verbose_name': 'произведение',
                'verbose_name_plural': 'произведения',
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('pub_date', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('score', models.IntegerField(default=10, validators=[django.core.validators.MaxValueValidator(10, message='оценка не может быть больше 10'), django.core.validators.MinValueValidator(1, message='оценка не может быть меньше 1')], verbose_name='оценка')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to=settings.AUTH_USER_MODEL, verbose_name='автор')),
                ('title', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviews', to='reviews.Title', verbose_name='произведение')),
            ],
            options={
                'verbose_name': 'отзыв',
                'verbose_name_plural': 'отзывы',
                'ordering': ['pub_date'],
            },
        ),
        migrations.AddField(
            model_name='genretitle',
            name='title',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='genre_titles', to='reviews.Title', verbose_name='произведение'),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='текст')),
                ('pub_date', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='дата публикации')),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comment', to=settings.AUTH_USER_MODEL, verbose_name='автор')),
                ('review', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='review_comments', to='reviews.Review', verbose_name='отзыв')),
            ],
            options={
                'verbose_name': 'комментарий',
                'verbose_name_plural': 'комментарии',
            },
        ),
        migrations.AddConstraint(
            model_name='review',
            constraint=models.UniqueConstraint(fields=('author', 'title'), name='unique_review'),
        ),
        migrations.AddConstraint(
            model_name='genretitle',
            constraint=models.UniqueConstraint(fields=('title', 'genre'), name='unique_GenreTitle'),
        ),
    ]
