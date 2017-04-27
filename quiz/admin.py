from django.contrib import admin
from quiz.models import *


class MultipleChoiceAnswerInline(admin.TabularInline):
    model = MultipleChoiceAnswer

class MultipleChoiceQuestionInline(admin.TabularInline):
    model = MultipleChoiceQuestion

class TrueFalseQuestionInline(admin.TabularInline):
    model = TrueFalseQuestion

class TextQuestionInline(admin.TabularInline):
    model = TextQuestion

class NumberQuestionInline(admin.TabularInline):
    model = NumberQuestion

class TopicInline(admin.TabularInline):
    model = Topic


@admin.register(MultipleChoiceQuestion)
class MultipleChoiceQuestionAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'question_text',
                'topic',
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
                'rating',
                'original_rating',
            ),
        }),
    )
    inlines = (
        MultipleChoiceAnswerInline,
    )


@admin.register(TextQuestion)
class TextQuestionAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'question_text',
                'answer',
                'topic',
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
                'rating',
                'original_rating',
            ),
        }),
    )

@admin.register(NumberQuestion)
class NumberQuestionAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'question_text',
                'answer',
                'topic',
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
                'rating',
                'original_rating',
            ),
        }),
    )


@admin.register(TrueFalseQuestion)
class TrueFalseQuestionAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'question_text',
                'answer',
                'topic',
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
                'rating',
                'original_rating',
            ),
        }),
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
        TrueFalseQuestionInline,
        MultipleChoiceQuestionInline,
        TextQuestionInline,
    )


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


class PlayerTopicInline(admin.TabularInline):
    model = PlayerTopic


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
                'title',
                'user',
            )
        }),
    )
    inlines = (
        TitleUnlockInline,
    )

@admin.register(PlayerAnswer)
class PlayerAnswerAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'player',
                'rating',
                'question',
                'result',
                'answer_date',
                'report_skip',
            )
        }),
    )

@admin.register(PlayerRating)
class PlayerRatingAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
           'fields': (
               'player',
               'subject',
               'rating',
           )
        }),
    )

class TitleInline(admin.TabularInline):
    model = Title


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'name',
                'badge',
            )
        }),
    )
    inlines = (
        TitleInline,
    )


@admin.register(Trigger)
class TriggerAdmin(admin.ModelAdmin):
    fieldsets=(
        (None, {
            'fields' : (
                'name',
                'properties',
            )
        }),
    )


@admin.register(PropAnsweredQuestionInSubject)
class PropAnswerdQuestionInSubjectAdmin(admin.ModelAdmin):
    fieldsets=(
        (None, {
            'fields' : (
                'name',
                'achievements',
                'number',
                'subject',
            )
        }),
    )


@admin.register(QuestionReport)
class QuestionReportAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'player',
                'question',
                'red_right',
                'green_wrong',
                'unclear',
                'off_topic',
                'inappropriate',
                'other',
                'comment',
            )
        }),
    )
