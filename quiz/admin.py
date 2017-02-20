from django.contrib import admin
from quiz.models import *


class MultipleChoiceAnswerInline(admin.TabularInline):
    model = MultipleChoiceAnswer


class QuestionTopicInline(admin.TabularInline):
    model = QuestionTopic


@admin.register(MultipleChoiceQuestion)
class MultipleChoiceQuestionAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'question_text',
            )
        }),
        ('Advanced options', {
            'classes': (
                'collapse',
                'closed',
            ),
            'fields': (
                'creator',
                'creation_date',
                'difficulty',
            ),
        }),
    )
    inlines = (
        MultipleChoiceAnswerInline,
        QuestionTopicInline,
    )


@admin.register(TextQuestion)
class TextQuestionAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'question_text',
                'answer',
            )
        }),
        ('Advanced options', {
            'classes': (
                'collapse',
                'closed',
            ),
            'fields': (
                'creator',
                'creation_date',
                'difficulty',
            ),
        }),
    )
    inlines = (
        QuestionTopicInline,
    )


@admin.register(TrueFalseQuestion)
class TrueFalseQuestionAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'question_text',
                'answer',
            )
        }),
        ('Advanced options', {
            'classes': (
                'collapse',
                'closed',
            ),
            'fields': (
                'creator',
                'creation_date',
                'difficulty',
            ),
        }),
    )
    inlines = (
        QuestionTopicInline,
    )


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'title',
                'subject',
            )
        }),
    )
    inlines = (
        QuestionTopicInline,
    )


class TopicInline(admin.TabularInline):
    model = Topic


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'code',
                'title',
                'short',
                'category',
            )
        }),
    )
    inlines = (
        TopicInline,
    )


class SubjectInline(admin.TabularInline):
    model = Subject


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'title',
            )
        }),
    )
    inlines = (
        SubjectInline,
    )


class PlayerInline(admin.TabularInline):
    model = Player


class TitleUnlockInline(admin.TabularInline):
    model = TitleUnlock


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'title',
                'achievement',
            )
        }),
    )
    inlines = (
        PlayerInline,
        TitleUnlockInline,
    )


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'regitration_date',
                'title',
                'skill_lvl',
                'user',
            )
        }),
    )
    inlines = (
        TitleUnlockInline,
    )


class TitleInline(admin.TabularInline):
    model = Title


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'name',
            )
        }),
    )
    inlines = (
        TitleInline,
    )
