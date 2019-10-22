from __future__ import absolute_import

import pytest
from sentry.testutils import TestCase
from clims.services import ProjectBase, SubstanceBase, FloatField, TextField, IntField
from clims.models.project import Project
from django.db import IntegrityError


class TestProject(TestCase):

    def setUp(self):
        self.register_extensible(VampireFangStudyProject)
        self.register_extensible(VampireFangSample)

    def test_can_create_project(self):
        project = VampireFangStudyProject(name="project1", organization=self.organization)
        project.save()
        Project.objects.get(name=project.name)  # Raises DoesNotExist if it wasn't created

    def test_name_is_unique(self):
        project = VampireFangStudyProject(name="project1", organization=self.organization)
        project.save()
        project2 = VampireFangStudyProject(name=project.name, organization=self.organization)
        with pytest.raises(IntegrityError):
            project2.save()

    def test_can_add_custom_property(self):
        project = VampireFangStudyProject(name="project1", organization=self.organization)
        project.comment = "test"
        project.save()

        model = Project.objects.get(id=project.id)
        project_fetched_again = self.app.projects.to_wrapper(model)
        assert project.comment == project_fetched_again.comment

    def test_can_add_sample(self):
        project = VampireFangStudyProject(name="project1", organization=self.organization)
        project.save()
        sample = VampireFangSample(name="sample1", organization=self.organization, project=project)
        sample.pointiness = 10.0
        sample.save()
        assert sample.project.name == project.name


class VampireFangStudyProject(ProjectBase):
    species = TextField("species")
    country_of_sampling = TextField("country_of_sampling")
    pi = TextField("pi")
    number_of_vampires_to_sample = IntField("number_of_vampires_to_sample")
    # TODO I guess maybe in the long run we need something smarter for comments in general
    #      in the long run they need to be sorted, associated with users, etc... /JD 2019-10-23
    comment = TextField("comment")


class VampireFangSample(SubstanceBase):
    pointiness = FloatField("pointiness")
