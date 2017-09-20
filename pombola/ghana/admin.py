from django.contrib import admin
from pombola.core.admin import PersonAdmin
from pombola.images.admin import ImageAdminInline
from .models import MP, GhanaMP


class MPInline(admin.StackedInline):
    model = MP
    fieldsets = (
       ('Other Personal Info', {
           'fields': [('first_name', 'last_name', 'middle_name'),
                      ('occupation', 'marital_status', 'hometown'),
                      ('education', 'religion', 'last_employment')]
       }),
       ('Political Info', {
           'fields': ('party_position', 'parliament_position',
                      'votes_obtained')
       }),
   )
    max_num = 1


class GhanaMPAdmin(PersonAdmin):
    prepopulated_fields = {"slug": ["legal_name"]}
    list_display = [
      'slug',
      'title',
      'legal_name',
      'gender',
    ]
    search_fields = ['legal_name']
    list_filter = ['gender', 'can_be_featured']

    fieldsets = (
       ('Personal Info', {
           'fields': [('title', 'legal_name'),
                      ('gender'),
                      ('date_of_birth', 'date_of_death'),
                      ('email', 'slug'),
                      ('can_be_featured', 'hidden'),
                      'summary',
                      ],
           'classes': ('extrapretty'),

       }),
       ('Other Info', {
           'fields': [
                      'national_identity',
                      ('honorific_prefix', 'honorific_suffix'),
                      ('family_name', 'given_name'),
                      ('additional_name' , 'sort_name'),
                      'biography',
                      ],
           'classes': ['collapse', 'extrapretty']
       }),
   )

    inlines = [
      MPInline,
      ImageAdminInline,
    ]

    class Meta:
        app_label = 'Ghana'


admin.site.register(GhanaMP, GhanaMPAdmin)
